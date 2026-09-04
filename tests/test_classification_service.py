import pytest

from bookmatch.services.classification_service import ClassificationService


def test_classification_service_cannot_be_instantiated():
    with pytest.raises(TypeError):
        ClassificationService()