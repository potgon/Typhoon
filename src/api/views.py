import os
import json
from confluent_kafka import KafkaException

from utils.logger import make_log
from kafka.services import delivery_callback, KafkaProducerSingleton
from ..database.models import ModelType, TrainedModel


class ListModelTypeView(GenericViewSet, ListModelMixin):
    queryset = ModelType.objects.all()
    serializer_class = ModelTypeSerializer

    def list(self, request, *args, **kwargs):
        return super(ListModelTypeView, self).list(request, *args, **kwargs)


class ListTrainedModelsView(GenericViewSet, ListModelMixin):
    queryset = TrainedModel
    serializer_class = TrainedModelSerializer

    def list(self, request, *args, **kwargs):
        return super(ListTrainedModelsView, self).list(request, *args, **kwargs)


class TrainModelView(GenericViewSet, CreateModelMixin):
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        asset_serializer = AssetSerializer(data=request.data)
        model_serializer = ModelTypeSerializer(data=request.data)

        if not asset_serializer.is_valid() or not model_serializer.is_valid():
            asset_id = asset_serializer.validated_data["id"]
            model_type_id = model_serializer.validated_data["id"]
            user_id = request.user.id

            return Response(
                {"message": "Asset/Model could not be validated"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            msg = json.dumps(
                {
                    "user_id": user_id,
                    "asset_id": asset_id,
                    "model_type_id": model_type_id,
                }
            )

            try:
                producer = KafkaProducerSingleton().get_producer()
            except KafkaException as ke:
                make_log(
                    "KAFKA",
                    40,
                    "kafka_models.log",
                    f"Error creating Kafka producer: {str(ke.args[0])}",
                )
                return Response(
                    {"message": "Error sending train request"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            try:
                topic = os.getenv("MODEL_QUEUE_TRAIN_TOPIC")
                producer.produce(topic, msg.encode("utf-8"), callback=delivery_callback)
                producer.flush()

                producer.close()
            except KafkaException as ke:
                make_log(
                    "KAFKA",
                    40,
                    "kafka_models.log",
                    f"Error producing message to topic: {str(ke.args[0])}",
                )
                return Response(
                    {"message": "Error sending train request"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {"message": "Model training request sent to Kafka"},
                status=status.HTTP_201_CREATED,
            )
