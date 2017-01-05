#!/bin/env python3

class BadRequestException(Exception):
	pass

class WordNotFoundException(Exception):
	pass

class AuthenticationError(Exception):
	pass

class ServiceUnavailableError(Exception):
	pass

class UnsupportedLanguageException(Exception):
	pass
