from django.db import models


class GroupPointsTransfer(models.Model):
    """ Prenaseni bodu mezi skupinami """
    src = models.ForeignKey('Group', on_delete=models.CASCADE, related_name="points_transfer_src")
    dest = models.ForeignKey('Group', on_delete=models.CASCADE, related_name="points_transfer_dst")
