
## file1.py

### Задача
Приложение подразумевает ежедневный вход пользователя, начисление баллов за вход. Нужно отследить момент первого входа игрока для аналитики. Также у игрока имеются игровые бонусы в виде нескольких типов бустов. Нужно описать модели игрока и бустов с возможностью начислять игроку бусты за прохождение уровней или вручную. (Можно написать, применяя sqlachemy)

### Решение
Файл содержить следующие классы моделей:
- Модель игрога **Player**
Модель игрока включает несколько полей: 
никнейм, почта, дата и время создания
```Python
    nickname = models.CharField(max_length=254, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
Некоторые игровые параметы: сила, ловкость

```Python
    power = models.PositiveIntegerField(default=0)
    agility = models.PositiveIntegerField(default=0)
```
И параметры, связанные со входом в игру
```Python
    status = models.CharField(max_length=56, choices=STATUS_CHOICES, default="NOT")
    entry_at = models.DateTimeField(null=True)
    points = models.PositiveIntegerField(default=0)
```
Поле status отображает вход пользователя в игру, его значения ограничены "EN" - игрок вошел в игру, "NOT" - игрок еще не входил в игру. В приложении может быть реализовано ежедневное сбрасывание пармаетра входа после истечения какого-либо срока или другие механизмы. Поле entry_at отражает дату и время входа пользователя в игру и может быть испоьзовано для аналитики. Поле points - число баллов.
- модели бонусов **BoostPower** и **BoostAgility**
Модели содержат очки модификации соответствующих параметров силы или ловкости, а также поле foreign key, которое ссылваетя на конкретного игрока.
```Python
    modification_points = models.PositiveIntegerField()

    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="boosts_power"
    )
```

Модель Player содержат два метода, отражающих вход игрока в игру и начисление бонусов:
- **entry()**
Метод entry используется при входе пользователя, он изменяет статус игрока на "EN" - вошел в игру, начисляет 200 дополнительных баллов, перезаписывает поле  entry_at значением текущего времени.
```Python
    def entry(self):
        self.status = "EN"
        self.points += 200
        self.entry_at = datetime.datetime.now(datetime.UTC)
        super().save()
```
- **add_boosts_for_levelup()**
Метод add_boosts_for_levelup используется для начисления бонусов (например за повышение уровня). В нем создаются объекты моделей бонусов с некоторыми значениями очков модификации.

## file2.py
### Задача
Даны модели:
```Python
from django.db import models

class Player(models.Model):
    player_id = models.CharField(max_length=100)
    
    
class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    
    
    
class Prize(models.Model):
    title = models.CharField()
    
    
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
```

Написать два метода:

1. Присвоение игроку приза за прохождение уровня.
2. Выгрузку в csv следующих данных: id игрока, название уровня, пройден ли уровень, полученный приз за уровень. Учесть, что записей может быть 100 000 и более.

### Решение
- метод **complete_level**
Метод используется при завершении уровня. Подразумевается, что в базе данных имеется запись игрока, запись уровня, запись приза за завершение уровня, а также запись прохождения уровня игроком модели PlayerLevel.
Метод принимает значения в качестве параметров: player_id - идентификатор игрока, level_id - идентификатор уровня, который необходимо отметить как завершенный, prize_id - идентификатор приза за завершение этого уровня.
Метод получает из базы данных запись связи игрока с уровнем (PlayerLevel). Заносит в поле completed - текущую дату и время, в поле is_completed - True (Отметка о завершении уровня)
```Python
    player_level = PlayerLevel.objects.get(player_id=player_id, level_id=level_id)
    player_level.completed = datetime.datetime.now(datetime.UTC)
    player_level.is_completed = True
    player_level.save()
```
Замет метод создает запись в таблице базы данных, связанной с моделью LevelPrize
```Python
    LevelPrize.objects.create(
        level_id=level_id,
        prize_id=prize_id,
        received=datetime.datetime.now(datetime.UTC),
    )
```

- метод **export_csv**
Метод используется для выгрузки из базы данных и записи его в файл формата csv. Сначала метод создает запрос в базу данных для получения объектов игрока, а также связанных с ним объектов уровней и призов. Используется метод prefetch_related, который в момент исполнения запроса позволит получить связанные объекты. Также для оптимизации используется метод iterator(), которые позволяет в случае наличия большого объема данных в базе получать результат по частям (параметр chunk_size установлен в значение 100).
```Python
    players_qs = Player.objects.prefetch_related(
        "playerlevel_set__level__levelprize_set__prize"
    ).iterator(chunk_size=100)
```
Открывается на запись файл "export_players.csv. В файл записываются данные игрока и объектов, связанных с ним: "player_id" - идентификатор игрока, "level" - название уровня, который выполняет или выполнил игрок, "level_is_completed" - true если игрок выполнил уровень, false - усли нет, "prize" - название приза или значение "не получен" если приз не получен игроком.
```Python
    with open("export_players.csv", "w") as f:
            export_writer = csv.writer(f, delimiter=";")
            export_writer.writerow(["player_id", "level", "level_is_completed", "prize"])

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
```

Пример файла **export_players.csv**:
```Csv
player_id;level;level_is_completed;prize
1;First level;True;For first level
1;Second level;False;не получен
2;First level;True;For first level
3;Second level;False;не получен
4;Third level;False;не получен
5;Third level;True;For third level
...
```
