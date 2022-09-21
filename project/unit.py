from __future__ import annotations
from abc import ABC, abstractmethod
from project.equipment import Weapon, Armor
from project.classes import UnitClass
from random import randint
from typing import Optional


class BaseUnit(ABC):
    """
    Базовый класс для любого юнита
    """
    def __init__(self, name: str, unit_class: UnitClass):
        """
        При инициализации класс Unit берет на себя свойства класса UnitClass
        """
        self.name = name
        self.unit_class = unit_class
        self.hp = unit_class.max_health
        self.stamina = unit_class.max_stamina
        self.weapon = None
        self.armor = None
        self._is_skill_used = False

    @property
    def health_points(self):
        """
        Возвращает значение здоровья hp в округленном виде
        """
        return round(self.hp, 1)

    @property
    def stamina_points(self):
        """
        Возвращает значение выносливости stamina в округленном виде
        """
        return round(self.stamina, 1)

    def equip_weapon(self, weapon: Weapon):
        """
        Присваивает герою выбранное оружие
        """
        self.weapon = weapon
        return f"{self.name} экипирован оружием {self.weapon.name}"

    def equip_armor(self, armor: Armor):
        """
        Присваивает герою выбранную броню
        """
        self.armor = armor
        return f"{self.name} экипирован броней {self.armor.name}"

    def _count_damage(self, target: BaseUnit) -> int:
        """
        Счетчик урона, брони, выносливости атакующего и защищающегося,
        а также возвращает конечный урон для вывода в текстовом виде
        """
        self.stamina -= self.weapon.stamina_per_hit * self.unit_class.stamina
        damage = self.weapon.damage * self.unit_class.attack
        if target.stamina > target.armor.stamina_per_turn * target.unit_class.stamina:
            target.stamina -= target.armor.stamina_per_turn * target.unit_class.stamina
            damage -= target.armor.defence * target.unit_class.armor
        return target.get_damage(damage)

    def get_damage(self, damage: int) -> Optional[int]:
        """
        Счетчик урона персонажу
        """
        self.hp = round(self.hp - damage, 1)
        if self.hp < 0:
            self.hp = 0
        return self.hp

    @abstractmethod
    def hit(self, target: BaseUnit) -> str:
        """
        Заглушка-метод для дальнейшего переопределения
        """
        pass

    def use_skill(self, target: BaseUnit) -> str:
        """
        Применение умения.
        Если использовано, то возвращаем строку "Навык использован"
        Если нет - выполняем функцию ниже
        self.unit_class.skill.use(user=self, target=target),
        возвращающую строку о выполнении умения
        """
        if self._is_skill_used:
            return "Навык уже был использован"
        else:
            if self.unit_class.skill._is_stamina_enough:
                self._is_skill_used = True
            return self.unit_class.skill.use(user=self, target=target)


class PlayerUnit(BaseUnit):
    """
    Класс "игрок"
    """
    def hit(self, target: BaseUnit) -> str:
        """
        Функция удар игрока:
        Происходит проверка выносливости для нанесения удара.
        Вызывается функция self._count_damage(target)
        Возвращается строкой результат
        """
        if self.stamina * self.unit_class.stamina >= self.weapon.stamina_per_hit:
            damage = round((self.hp - self._count_damage(target)), 2)
            if damage > 0:
                return f"{self.name} используя {self.weapon.name} пробивает {target.armor.name} соперника и наносит {damage} урона."
            else:
                return f"{self.name} используя {self.weapon.name} наносит удар, но {target.armor.name} cоперника его останавливает."
        else:
            f"{self.name} попытался использовать {self.weapon.name}, но у него не хватило выносливости."


class EnemyUnit(BaseUnit):
    """
    Класс "враг"
    """
    def hit(self, target: BaseUnit) -> str:
        """
        Функция удар врага должна содержать логику применения соперником умения
        (он должен делать это автоматически и только 1 раз за бой).
        Для этих целей используется функция Randint из библиотеки Random.
        Если умение не применено, противник наносит простой удар, где также используется
        функция _count_damage(target)
        """
        if not self._is_skill_used and self.stamina >= self.unit_class.skill.stamina and randint(0, 100) < 10:
            return self.use_skill(target)

        if self.stamina * self.unit_class.stamina < self.weapon.stamina_per_hit:
            return f"\n {self.name} попытался использовать {self.weapon.name}, но у него не хватило выносливости."

        damage = self._count_damage(target)
        if damage > 0:
            return f"\n{self.name} используя {self.weapon.name} пробивает {target.armor.name} и наносит Вам {damage} урона. "

        return f"\n{self.name} используя {self.weapon.name} наносит удар, но Ваш {target.armor.name}  его  останавливает."
