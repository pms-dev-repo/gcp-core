from __future__ import annotations

from services.openflights_service import sync_all


def main() -> None:
    result = sync_all()
    print("OpenFlights synchronization completed")
    print(f"Airports: {result['airports']:,}")
    print(f"Airlines: {result['airlines']:,}")
    print(f"Routes:   {result['routes']:,}")


if __name__ == "__main__":
    main()
