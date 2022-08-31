import random


class TauntsGenerator:
    taunts_arr = ["aidaev pidar", "smagin gandon", "putin huylo", "rusni pizda"]

    def generate_some_taunts(self):
       return self.taunts_arr[random.randrange(0, len(self.taunts_arr))]