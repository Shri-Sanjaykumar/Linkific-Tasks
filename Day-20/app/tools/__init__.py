"""
Day 20 — Tools Package
Exposes all 8 core tools and the Company Project Practical tool,
plus helper to register all tools into a registry.
"""

from .calculator import calculator_tool, CALCULATOR_DEFINITION
from .web_search import web_search_tool, WEB_SEARCH_DEFINITION
from .database_tool import database_tool, DATABASE_DEFINITION
from .file_reader import file_reader_tool, FILE_READER_DEFINITION
from .weather_tool import weather_tool, WEATHER_DEFINITION
from .email_tool import email_tool, EMAIL_DEFINITION
from .date_tool import date_tool, DATE_DEFINITION
from .data_analyzer import data_analyzer_tool, DATA_ANALYZER_DEFINITION
from .company_search import company_search_tool, COMPANY_SEARCH_DEFINITION
from .pdf_reader import pdf_reader_tool, PDF_READER_DEFINITION


def register_all_tools(registry):
    """Registers all 10 tools (8 core + 2 company project practical tools) into the provided registry."""
    registry.register(CALCULATOR_DEFINITION, calculator_tool)
    registry.register(WEB_SEARCH_DEFINITION, web_search_tool)
    registry.register(DATABASE_DEFINITION, database_tool)
    registry.register(FILE_READER_DEFINITION, file_reader_tool)
    registry.register(WEATHER_DEFINITION, weather_tool)
    registry.register(EMAIL_DEFINITION, email_tool)
    registry.register(DATE_DEFINITION, date_tool)
    registry.register(DATA_ANALYZER_DEFINITION, data_analyzer_tool)
    registry.register(COMPANY_SEARCH_DEFINITION, company_search_tool)
    registry.register(PDF_READER_DEFINITION, pdf_reader_tool)
