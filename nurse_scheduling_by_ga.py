# -*- coding: utf-8 -*-
import random
from scoop import futures

from deap import base
from deap import creator
from deap import tools
from deap import cma
import xlwings as xw


# 従業員人数
EMPLOYEE_COUNT = 8

# シフトの数
SHIFT_NUM = 28

# 次元数
DIM = SHIFT_NUM * EMPLOYEE_COUNT



# 従業員を表すクラス
class Employee(object):
  def __init__(self, no, name, age, manager, rests):
    self.no = no
    self.name = name
    self.age = age
    self.manager = manager

    # willは曜日_時間帯。1は朝、2は昼、3は夜。
    # 例）mon_1は月曜日の朝
    self.rests = rests

  def __str__(self):
    return '{}: {}'.format(self.no, '/'.join(self.rests))

  def is_applicated(self, box_name):
    return (box_name not in self.rests)

# シフトを表すクラス
# 内部的には SHIFT_NUM * EMPLOYEE_COUNT人 = x次元のタプルで構成される
class Shift(object):
  # コマの定義

  # とりあえず1 ~ 7日
  SHIFT_BOXES = [
    'month1_d', 'month1_d8', 'month1_d11', 'month1_n', 
    'month2_d', 'month2_d8', 'month2_d11', 'month2_n', 
    'month3_d', 'month3_d8', 'month3_d11', 'month3_n', 
    'month4_d', 'month4_d8', 'month4_d11', 'month4_n', 
    'month5_d', 'month5_d8', 'month5_d11', 'month5_n', 
    'month6_d', 'month6_d8', 'month6_d11', 'month6_n',
    'month7_d', 'month7_d8', 'month7_d11', 'month7_n',
  ]


  # 各コマの想定人数
  NEED_PEOPLE = [
    3,1,1,3,
    3,1,1,3,
    3,1,1,3,
    3,1,1,3,
    3,1,1,3,
    3,1,1,3,
    3,1,1,3
  ]


  def __init__(self, list):
    if list == None:
      self.make_sample()
    else:
      self.list = list
    self.employees = []

  # ランダムなデータを生成
  def make_sample(self):
    sample_list = []
    for num in range(DIM):
      sample_list.append(random.randint(0, 1))
    self.list = tuple(sample_list)

  # タプルを1ユーザ単位に分割
  def slice(self):
    sliced = []
    start = 0
    for num in range(EMPLOYEE_COUNT):
      sliced.append(self.list[start:(start + SHIFT_NUM)])
      start = start + 21
    return tuple(sliced)

  # ユーザ別にアサインコマ名を出力する
  def print_inspect(self):
    user_no = 0
    for line in self.slice():
      print("ユーザ%d" % user_no)
      print(line)
      user_no = user_no + 1

      index = 0
      for e in line:
        if e == 1:
          print(self.SHIFT_BOXES[index])
        index = index + 1

  # CSV形式でアサイン結果の出力をする
  def print_csv(self):
    for line in self.slice():
      print(','.join(map(str, line)))

  # TSV形式でアサイン結果の出力をする
  def print_tsv(self):
    for line in self.slice():
      print("\t".join(map(str, line)))

  # ユーザ番号を指定してコマ名を取得する
  def get_boxes_by_user(self, user_no):
    line = self.slice()[user_no]
    return self.line_to_box(line)

  # 1ユーザ分のタプルからコマ名を取得する
  def line_to_box(self, line):
    result = []
    index = 0
    for e in line:
      if e == 1:
        result.append(self.SHIFT_BOXES[index])
      index = index + 1
    return result    

  # コマ番号を指定してアサインされているユーザ番号リストを取得する
  def get_user_nos_by_box_index(self, box_index):
    user_nos = []
    index = 0
    for line in self.slice():
      if line[box_index] == 1:
        user_nos.append(index)
      index += 1
    return user_nos

  # コマ名を指定してアサインされているユーザ番号リストを取得する
  def get_user_nos_by_box_name(self, box_name):
    box_index = self.SHIFT_BOXES.index(box_name)
    return self.get_user_nos_by_box_index(box_index)

  # 想定人数と実際の人数の差分を取得する
  def abs_people_between_need_and_actual(self):
    result = []
    index = 0
    for need in self.NEED_PEOPLE:
      actual = len(self.get_user_nos_by_box_index(index))
      result.append(abs(need - actual))
      index += 1
    return result

  # 応募していないコマにアサインされている件数を取得する
  def not_applicated_assign(self):
    count = 0
    for box_name in self.SHIFT_BOXES:
      user_nos = self.get_user_nos_by_box_name(box_name)
      for user_no in user_nos:
        e = self.employees[user_no]
        if not e.is_applicated(box_name):
          count += 1
    return count

  # アサインが応募コマ数の50%に満たないユーザを取得
  def few_work_user(self):
    result = []
    for user_no in range(EMPLOYEE_COUNT):
      e = self.employees[user_no]
      # ratio = float(len(self.get_boxes_by_user(user_no))) / float(len(e.rests))
      if ratio < 0.5:
        result.append(e)
    return result

  # 管理者が1人もいないコマ
  def no_manager_box(self):
    result = []
    for box_name in self.SHIFT_BOXES:
      manager_included = False
      user_nos = self.get_user_nos_by_box_name(box_name)
      for user_no in user_nos:
        e = self.employees[user_no]
        if e.manager:
          manager_included = True
      if not manager_included:
        result.append(box_name)
    return result

  # 1日1人4コマの日を返却
  def four_box_per_day(self):
    result = []
    for user_no in range(EMPLOYEE_COUNT):
      boxes = self.get_boxes_by_user(user_no)
      wdays = []
      for box in boxes:
        wdays.append(box.split('_')[0])
      wday_names = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
      for wday_name in wday_names:
        if wdays.count(wday_name) == 3:
          result.append(wday_name)
    return result

  @classmethod
  def make_shift_day(self, num):
    return 'month{0}_d//month{0}_d8//month{0}_d11//month{0}_n'.format(num).split('//')

# 従業員定義

# excelのやつ
wb = xw.Book('test.xlsx')
sht5 = wb.sheets['Sheet5']
sht6 = wb.sheets['Sheet6']

employees_dict = {}

for i in range(EMPLOYEE_COUNT):
    employee_name = sht6.range('A' + str(i + 4)).value
    employee_id = int(sht6.range('B' + str(i + 4)).value)
    employees_dict[employee_id] = Employee(employee_id, employee_name, 0, False, [])

for i in range(7):
  id1 = int(sht5.range('G' + str(i + 6)).value)
  id2 = int(sht5.range('H' + str(i + 6)).value)
  employees_dict[id1].rests.extend(Shift.make_shift_day(i+1))
  employees_dict[id2].rests.extend(Shift.make_shift_day(i+1))


for k, v in employees_dict.items():
  print(v.no, v.rests)


employees = list(employees_dict.values())


creator.create("FitnessPeopleCount", base.Fitness, weights=(-100.0, -100.0))
creator.create("Individual", list, fitness=creator.FitnessPeopleCount)

toolbox = base.Toolbox()

toolbox.register("map", futures.map)

toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, DIM)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalShift(individual):
  s = Shift(individual)
  s.employees = employees

  # 想定人数とアサイン人数の差
  people_count_sub_sum = 1.0 * sum(s.abs_people_between_need_and_actual()) / DIM

  # 応募していない時間帯へのアサイン数
  not_applicated_count = s.not_applicated_assign() / 1.0 * DIM

  return (people_count_sub_sum, not_applicated_count)

toolbox.register("evaluate", evalShift)
# 交叉関数を定義(二点交叉)
toolbox.register("mate", tools.cxTwoPoint)

# 変異関数を定義(ビット反転、変異隔離が5%ということ?)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)

# 選択関数を定義(トーナメント選択、tournsizeはトーナメントの数？)
toolbox.register("select", tools.selTournament, tournsize=3)





if __name__ == '__main__':


    # 初期集団を生成する
    pop = toolbox.population(n=300)
    CXPB, MUTPB, NGEN = 0.6, 0.5, 100 # 交差確率、突然変異確率、進化計算のループ回数

    print("進化開始")

    # 初期集団の個体を評価する
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):  # zipは複数変数の同時ループ
        # 適合性をセットする
        ind.fitness.values = fit

    print("  %i の個体を評価" % len(pop))

     # 進化計算開始
    for g in range(NGEN):
        print("-- %i 世代 --" % g)

        # 選択
        # 次世代の個体群を選択
        offspring = toolbox.select(pop, len(pop))
        # 個体群のクローンを生成
        offspring = list(map(toolbox.clone, offspring))

        # 選択した個体群に交差と突然変異を適応する

        # 交叉
        # 偶数番目と奇数番目の個体を取り出して交差
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                # 交叉された個体の適合度を削除する
                del child1.fitness.values
                del child2.fitness.values

        # 変異
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # 適合度が計算されていない個体を集めて適合度を計算
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        print("  %i の個体を評価" % len(invalid_ind))

        # 次世代群をoffspringにする
        pop[:] = offspring

        # すべての個体の適合度を配列にする
        index = 1
        for v in ind.fitness.values:
          fits = [v for ind in pop]

          length = len(pop)
          mean = sum(fits) / length
          sum2 = sum(x*x for x in fits)
          std = abs(sum2 / length - mean**2)**0.5

          print("* パラメータ%d" % index)
          print("  Min %s" % min(fits))
          print("  Max %s" % max(fits))
          print("  Avg %s" % mean)
          print("  Std %s" % std)
          index += 1

    print("-- 進化終了 --")

    best_ind = tools.selBest(pop, 1)[0]
    print("最も優れていた個体: %s, %s" % (best_ind, best_ind.fitness.values))
    s = Shift(best_ind)
    s.print_csv()
    s.print_tsv()
