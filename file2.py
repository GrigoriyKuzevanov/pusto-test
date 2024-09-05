import csv
import datetime

from django.db import models


class Player(models.Model):
    # player_id = models.CharField(max_length=100)
    pass


class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)


class Prize(models.Model):
    title = models.CharField(max_length=100)


class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField()
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)


class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField()


def complete_level(player_id, level_id, prize_id):
    """
    Метод выполнения уровня
    """
    # Изменение параметров записи игрок_уровень
    player_level = PlayerLevel.objects.get(player_id=player_id, level_id=level_id)
    player_level.completed = datetime.datetime.now(datetime.UTC)
    player_level.is_completed = True
    player_level.save()

    # Создание записи полученя приза за уровень
    LevelPrize.objects.create(
        level_id=level_id,
        prize_id=prize_id,
        received=datetime.datetime.now(datetime.UTC),
    )


def export_csv():
    """
    Метод экспорта csv файла
    """
    # Для экономии ресурсов используется метод iterator для запроса, также используется метод prefetch_related для
    # загрузки всех связанных объектов и их связывания в Python
    players_qs = Player.objects.prefetch_related(
        "playerlevel_set__level__levelprize_set__prize"
    ).iterator(chunk_size=100)

    # открытие файлы для записи
    with open("export_players.csv", "w") as f:
        export_writer = csv.writer(f, delimiter=";")
        export_writer.writerow(["player_id", "level", "level_is_completed", "prize"])

        # для каждого объекта игрока из запроса проходим по
        # связанным с ним объектам уровней и призов,
        # если уровень пройден - записывем данные приза,
        # если уровень не пройден - записываем в поле приза "не получен"
        for player in players_qs:
            player_id = player.id

            for player_level in player.playerlevel_set.all():
                level = player_level.level.title
                level_is_completed = player_level.is_completed

                if level_is_completed:
                    level_prize = player_level.level.levelprize_set.filter(
                        level_id=player_level.level_id
                    ).first()
                    prize = level_prize.prize.title
                    export_writer.writerow(
                        [player_id, level, level_is_completed, prize]
                    )

                else:
                    export_writer.writerow(
                        [player_id, level, level_is_completed, "не получен"]
                    )
