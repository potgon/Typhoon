from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=30, unique=True)
    password = fields.CharField(max_length=128)
    email = fields.CharField(max_length=50, unique=True)
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)
    date_joined = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    priority = fields.BooleanField(default=False)
    tokens = fields.IntField(default=0)

    def __str__(self):
        return f"{self.username} - {self.email}"


class ModelType(Model):
    id = fields.IntField(pk=True)
    model_name = fields.CharField(max_length=50, unique=True)
    description = fields.TextField()
    default_hyperparameters = fields.JSONField()
    default_model_architecture = fields.TextField()

    def __str__(self):
        return self.model_name


class TrainedModel(Model):
    model_type = fields.ForeignKeyField(
        "models.ModelType",
        null=True,
        related_name="model_type",
        on_delete=fields.NO_ACTION,
    )
    user = fields.ForeignKeyField(
        "models.User", null=True, related_name="user", on_delete=fields.CASCADE
    )
    asset = fields.ForeignKeyField(
        "models.Asset", null=True, related_name="asset", on_delete=fields.NO_ACTION
    )
    model_name = fields.CharField(max_length=50)
    training_timestamp = fields.DatetimeField(auto_now_add=True)
    performance_metrics = fields.JSONField()
    hyperparameters = fields.JSONField()
    model_architecture = fields.TextField()
    serialized_model = fields.BinaryField()
    training_logs = fields.TextField()
    status = fields.CharField(max_length=25, default="Inactive")

    def __str__(self):
        return self.model_name


class Queue(Model):
    user = fields.ForeignKeyField(
        "models.User", related_name="user", on_delete=fields.CASCADE
    )
    asset = fields.ForeignKeyField(
        "models.Asset", related_name="asset", on_delete=fields.CASCADE
    )
    model_type = fields.ForeignKeyField(
        "models.ModelType", related_name="model_type", on_delete=fields.CASCADE
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    priority = fields.BooleanField(default=False)

    class Meta:
        ordering = ["priority", "created_at"]

    def __str__(self):
        return (
            f"{self.user.username} - {self.asset.name} - {self.model_type.model_name}"
        )
