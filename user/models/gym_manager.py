from user.models.base_profile import BaseProfile


class GymManager(BaseProfile):
    def __str__(self):
        return self.user.name + " " + self.gym.name
