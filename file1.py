import datetime

from django.db import models


class Player(models.Model):
    """
    Примерная модель игрока
    """

    STATUS_CHOICES = [
        ("EN", "Entry had been completed"),
        ("NOT", "Entry had't been completed yet"),
    ]

    # Общая информция об игроке
    nickname = models.CharField(max_length=254, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Игровые параметры
    power = models.PositiveIntegerField(default=0)
    agility = models.PositiveIntegerField(default=0)

    # Пармаетры, связанные со входом игрока в игру
    status = models.CharField(max_length=56, choices=STATUS_CHOICES, default="NOT")
    entry_at = models.DateTimeField(null=True)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nickname}"

    def entry(self):
        """
        При входе, меняется статус игрока, начисляются баллы,
        фиксируется время входа
        """
        self.status = "EN"
        self.points += 200
        self.entry_at = datetime.datetime.now(datetime.UTC)
        super().save()

    def add_boosts_for_levelup(self):
        """
        Добавление бустов при повышении уровня
        """
        self.boosts_power.create(modification_points=300)
        self.boosts_agility.create(modification_points=250)


class BoostPower(models.Model):
    """
    Модель буста силы
    """

    modification_points = models.PositiveIntegerField()

    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="boosts_power"
    )

    def __str__(self):
        return f"{self.player.nickname} {self.modification_points}"


class BoostAgility(models.Model):
    """
    Модель буста ловкости
    """

    modification_points = models.PositiveIntegerField()

    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="boosts_agility"
    )

    def __str__(self):
        return f"{self.player.nickname} {self.modification_points}"
