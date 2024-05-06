"""

This code is only for testing genetics and should not be used in bots.

This can be run inside the interactive console to view variables.

"""
from typing import List

from genetics.family import Member
from genetics.grader.roleplay import Attributes, grade_entity
from genetics.survival import Survival, Survivor


def get_score(survivor: Survivor):
    return survivor.points


def get_nearest_score(survivor: Survivor, offset=0.0):
    return abs(survivor.points - offset)


def main(years=100):
    history: List[dict] = []
    best_survivors: List[Survivor] = []
    template = Attributes()
    game = Survival(template, 100, 2)
    game.generate()
    for i in range(years):
        survivors = game.population.survivors
        for survivor in survivors:
            if survivor.points > 0:
                continue
            points = grade_entity(survivor.entity)
            survivor.set_points(points)
        scores = game.evaluate()
        # scores.__dict__['performance'] = game.observer.progression() * 100

        survivors = game.survive()

        statistics = game.statistics()
        statistics['born*'] = game.reproduce()
        statistics['generated*'] = game.generate()

        best_survivor = max(survivors, key=get_score)
        worst_survivor = min(survivors, key=get_score)
        middle_survivor = min(survivors, key=lambda g: get_nearest_score(g, scores.middle))
        median_survivor = min(survivors, key=lambda g: get_nearest_score(g, scores.median))
        average_survivor = min(survivors, key=lambda g: get_nearest_score(g, scores.average))

        print(
            'Year', game.year, statistics, '\n',
            'Scores ', scores, '\n',
            'Best   ', best_survivor, '\n',
            'Average', average_survivor, '\n',
            'Median ', median_survivor, '\n',
            'Middle ', middle_survivor, '\n',
            'Worst  ', worst_survivor, '\n',
        )
        history.append(scores.__dict__)
        best_survivors.append(best_survivor)

    for year in range(years):
        if year % 50 != 0:
            continue
        name = best_survivors[year].entity.name
        genetics = best_survivors[year].entity.genetics
        print('Year:', year, 'Name:', name, genetics)
    #
    # import matplotlib.pyplot as plt
    # import pandas
    #
    # history.insert(0, {})
    # dataframe = pandas.DataFrame(history)
    #
    # dataframe.plot()
    # plt.show()
    return game


if __name__ == '__main__':
    data = main()

    foo_s = max(data.population.survivors, key=lambda e: e.points if type(e.entity) is Member else 0)
    foo_e = foo_s.entity
    foo_r = foo_e.relationships

    bar_s = max(data.population.survivors,
                key=lambda e: len(e.entity.relationships.ascendants) + len(e.entity.relationships.descendants)
                if type(e.entity) is Member else 0)
    bar_e = bar_s.entity
    bar_r = bar_e.relationships
