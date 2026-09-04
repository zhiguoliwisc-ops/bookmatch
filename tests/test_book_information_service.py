import pytest

from bookmatch.services.book_information_service import (
    BookInformationService,
)


def test_book_information_service_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BookInformationService()