from abc import ABC, abstractmethod
from typing import List, Dict, Type
from app.infrastructure.parsers.base import BaseStatementParser, TransactionRow

class IParserService(ABC):
    @abstractmethod
    def get_parser(self, bank_id: str, file_type: str) -> BaseStatementParser:
        """
        Returns the appropriate parser based on bank and file type.
        """
        pass

    @abstractmethod
    def parse_file(self, bank_id: str, file_type: str, file_content: bytes, filename: str) -> List[TransactionRow]:
        """
        Parses a file using the correct parser.
        """
        pass

class BankFileParserService(IParserService):
    def __init__(self):
        self._parsers: Dict[str, Type[BaseStatementParser]] = {}

    def register_parser(self, identifier: str, parser_class: Type[BaseStatementParser]):
        """
        Registers a parser class for a given identifier (e.g., 'banesco_excel').
        """
        self._parsers[identifier] = parser_class

    def get_parser(self, bank_id: str, file_type: str) -> BaseStatementParser:
        """
        Factory method to get a parser instance.
        """
        identifier = f"{bank_id}_{file_type}".lower()
        parser_class = self._parsers.get(identifier)
        if not parser_class:
            raise NotImplementedError(f"No parser registered for identifier '{identifier}'")
        return parser_class()

    def parse_file(self, bank_id: str, file_type: str, file_content: bytes, filename: str) -> List[TransactionRow]:
        parser = self.get_parser(bank_id, file_type)
        if not parser.validate_format(file_content, filename):
            raise ValueError(f"File '{filename}' is not in the correct format for the selected parser.")
        return parser.parse(file_content, filename)
