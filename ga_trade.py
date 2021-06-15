import numpy
import random
import operator
import pandas as pd

random.seed(a=None)


class Chromosome:
    """
    Описывает отдельную хромосому
    """

    def __init__(self, min=None, max=None, prev_min=None, prev_max=None, buy=None, score=None):
        """
        Конструктор класса
        """
        self.min = min
        self.max = max
        self.prev_min = prev_min
        self.prev_max = prev_max
        self.buy = buy
        self.score = score

    def mutate(self):
        """
        Метод, описывающий мутацию отдельной хромосомы (одного из генов в ней)
        """
        mu, sigma = 0, 0.15  # среднее и стандартное отклонение

        x = numpy.random.normal(mu, sigma, 1)[0]

        toChange = random.randint(0, 5)

        if toChange == 0:
            self.buy = random.randint(0, 999) % 2
        elif toChange == 1:
            self.min = next(x)
        elif toChange == 2:
            self.max = next(x)
        elif toChange == 3:
            self.prev_min = next(x)
        elif toChange == 4:
            self.prev_max = next(x)

        if self.min > self.max:
            self.min, self.max = self.max, self.min

        if self.prev_min > self.prev_max:
            self.prev_min, self.prev_max = self.prev_max, self.prev_min


class GeneticTraiding(object):
    """ Класс реализации алгоритма Мейера - Пакарда """
    population = []
    nextGeneration = []

    def __init__(self, **kwargs):
        self.popSize = kwargs['popSize']
        self.mRate = kwargs['mRate']
        self.mChange = kwargs['mChange']
        self.predictionN = kwargs['predictionN']
        cols = kwargs['df'].columns
        self.dayChange, self.nextDayChange, self.profit = kwargs['df'][cols[1]], \
                                                          kwargs['df'][cols[2]], \
                                                          kwargs['df'][cols[3]]

        self.datasize = len(self.dayChange)
        self.min_profit = min(self.profit)

    def populationInit(self):
        """
        Инициализация популяции
        с использованием генератора случайных чисел создается популяция заданного размера
        """

        mu, sigma = 0, 1.5  # mean and standard deviation
        s = numpy.random.normal(mu, sigma, 4 * self.popSize)

        x = iter(s)
        for i in range(self.popSize):
            temp = Chromosome(next(x), next(x), next(x), next(x), random.randint(0, 999) % 2, 0)

            # обмен местами минимума и максимума, если это необходимо
            if temp.min > temp.max:
                temp.min, temp.max = temp.max, temp.min
            if temp.prev_min > temp.prev_max:
                temp.prev_min, temp.prev_max = temp.prev_max, temp.prev_min

            # добавление сгенерированного гена в популяцию
            self.population.append(temp)

    def fitnessFunction(self):
        """Фитнес - функция (оценочная функция)
        Производит поиск в исторических данных нужных случаев
        и присваивает score = прибыль по найденному случаю
        Иначе 0
        """
        for i in range(len(self.population)):
            for j in range(self.datasize):
                if self.population[i].prev_min < self.dayChange[j] < self.population[i].prev_max:
                    if self.population[i].min < self.nextDayChange[j] < self.population[i].max:
                        if self.population[i].buy == 1:
                            self.population[i].score += self.profit[j]
                            break

                if self.population[i].prev_min < self.dayChange[j] < self.population[i].prev_max:
                    if self.population[i].min < self.nextDayChange[j] < self.population[i].max:
                        if self.population[i].buy == 0:
                            self.population[i].score -= self.profit[j]
                            break
            else:
                self.population[i].score = self.min_profit

    def weighted_random_choice(self):
        """
        Метод отбора хромосом
        """
        self.fitnessFunction()
        max = self.population[0].score
        for i in self.population[1:]:
            max += i.score
            pick = random.uniform(0, max)
            current = 0
            for i in range(len(self.population)):
                current += self.population[i].score
                if current > pick:
                    self.nextGeneration.append(self.population[i])

    def exists(self):
        """
        Служебная функция удаления особей с неоцененным фитнесом
        """
        i = 0
        while i < len(self.population):
            if self.population[i].score is None:
                del self.population[i]
            else:
                i += 1

    def uniformCross(self):
        """
        Метод, реализующий скрещивание
        """
        children = []

        for i in range(self.popSize - len(self.nextGeneration)):
            child = Chromosome(0, 0, 0, 0, 0)
            chromosome1 = self.nextGeneration[random.randint(0, 999999) % len(self.nextGeneration)]
            chromosome2 = self.nextGeneration[random.randint(0, 999999) % len(self.nextGeneration)]

            if random.randint(0, 999) % 2:
                child.min = chromosome1.min
            else:
                child.min = chromosome2.min

            if random.randint(0, 999) % 2:
                child.max = chromosome1.max

            else:
                child.max = chromosome2.max

            # обмен хромосом в случае нарушения неравества больше - меньше
            if child.max < child.min:
                child.max, child.min = child.min, child.max

            if random.randint(0, 999) % 2:
                child.prev_min = chromosome1.prev_min
            else:
                child.prev_min = chromosome2.prev_min

            if random.randint(0, 999) % 2:
                child.prev_max = chromosome1.prev_max
            else:
                child.prev_max = chromosome2.prev_max

            # обмен хромосом в случае нарушения неравества больше - меньше
            if child.prev_max < child.prev_min:
                child.prev_max, child.prev_min = child.prev_min, child.prev_max

            if random.randint(0, 999) % 2:
                child.buy = chromosome1.buy
            else:
                child.buy = chromosome2.buy

            # Append
            children.append(child)

        for i in range(len(children)):
            if random.randint(0, 999) % 100 <= self.mRate * 100:
                children[i].mutate()
            self.population[i] = children[i]

        for i in range(len(children), len(self.population), 1):
            self.population[i] = self.nextGeneration[i - len(children)]

        self.exists()
        self.fitnessFunction()
        self.population.sort(key=operator.attrgetter('score'))

    def returnResult(self):
        """
        Вывод результатов работы оценочного алгоритма
        """
        buyRec = []
        shortRec = []
        for i in range(len(self.population)):
            if self.population[i].buy == 1:
                buyRec.append(self.population[i])
            if self.population[i].buy == 0:
                shortRec.append(self.population[i])

        outputBuy = []
        outputShort = []

        i = 1
        size = len(buyRec)
        while i < self.predictionN + 1:
            index = size - i
            outputBuy.append(buyRec[index].score)
            i += 1

        i = 1
        size = len(shortRec)
        while i < self.predictionN + 1:
            index = size - i
            outputShort.append(shortRec[index].score)
            i += 1

        my_list = []
        for i in range(len(outputBuy)):
            if outputBuy[i] > outputShort[i]:
                my_list.append(1)
            else:
                my_list.append(0)

        avg = sum(my_list) / len(my_list)
        print("\n\nРезультат отбора правил", my_list)
        if avg >= 0.5:
            return True
        else:
            return False


def use_ga(df):
    x = GeneticTraiding(popSize=50, mRate=0.05, mChange=2, predictionN=5, df=df)
    x.populationInit()
    x.weighted_random_choice()
    x.uniformCross()
    return x.returnResult()

