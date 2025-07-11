# Referencja API

Ten dokument zawiera szczegółowy opis interfejsów programistycznych dostępnych w systemie OCR.

## Spis treści

1. [Interfejs wiersza poleceń](cli.md)
2. [API Pythona](python-api.md)
3. [Struktura projektu](project-structure.md)
4. [Formaty plików](file-formats.md)

## Przegląd

System oferuje kilka interfejsów programistycznych:

- **CLI** - wiersz poleceń do przetwarzania dokumentów
- **Python API** - moduły i klasy do integracji z innymi aplikacjami Pythona
- **Web API** - (planowane) REST API do zdalnego przetwarzania dokumentów

## Wersjonowanie

API korzysta z semantycznego wersjonowania (SemVer):

- **MAJOR** - niezgodne zmiany w API
- **MINOR** - nowe funkcje zachowujące wsteczną zgodność
- **PATCH** - poprawki błędów i optymalizacje

## Standardowe odpowiedzi

Wszystkie odpowiedzi zwracane przez API zawierają:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "metadata": {
    "version": "1.0.0",
    "timestamp": "2023-06-15T12:00:00Z"
  }
}
```

## Obsługa błędów

W przypadku błędu odpowiedź zawiera kod statusu HTTP i szczegóły błędu:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Nieprawidłowy format danych wejściowych",
    "details": {
      "field": "input_file",
      "issue": "Plik nie istnieje"
    }
  }
}
```

## Uwierzytelnianie

Dla wersji zdalnej (planowanej) wymagane będzie uwierzytelnianie za pomocą tokena API:

```
Authorization: Bearer twój_token_api
```

## Limity

- Maksymalny rozmiar pliku: 50MB
- Maksymalna liczba stron: 500
- Maksymalna liczba równoległych żądań: 10 na użytkownika

## Wsparcie

W przypadku pytań dotyczących API skontaktuj się z nami pod adresem support@wronai.com.
