# 🛋 Pillow Alert

Automatikus push értesítés, ha eső vagy erős szél várható — hogy időben behozhassuk a párnákat.

## Hogyan működik

Naponta kétszer (9:00 és 21:00) egy GitHub Actions workflow lekéri az időjárás-előrejelzést az [Open-Meteo](https://open-meteo.com/) API-ból, és ha szükséges, [Pushover](https://pushover.net/) értesítést küld mindkét felhasználónak.

- **Reggeli futás (9:00):** a következő 12 óra előrejelzése
- **Esti futás (21:00):** a következő nap teljes előrejelzése

## Riasztási feltételek

| Esemény | Küszöb |
|---|---|
| Eső | bármennyi csapadék |
| Széllökés | > 35 km/h |
| Alap szél | > 35 km/h |

Az értesítés tartalmazza a legsúlyosabb 2 szél/lökés eseményt (időponttal), valamint a legerősebb esőszakaszt (kezdés, összmennyiség, időtartam).

## Technológiák

- **[Open-Meteo](https://open-meteo.com/)** — ingyenes időjárás API, kulcs nélkül
- **[GitHub Actions](https://github.com/features/actions)** — ingyenes ütemezett futtatás
- **[Pushover](https://pushover.net/)** — iOS/Android push értesítés (egyszeri $5/fő)

## Beállítás

### 1. Pushover
1. Hozz létre fiókot a [pushover.net](https://pushover.net)-en
2. Hozz létre egy új alkalmazást → kapni fogsz egy **App Token**-t
3. Mindkét felhasználó telepítse a Pushover appot, és mentse el a saját **User Key**-jét

### 2. GitHub Secrets
A repo Settings → Secrets → Actions menüben add hozzá:

| Secret neve | Értéke |
|---|---|
| `PUSHOVER_TOKEN` | Az alkalmazás App Token-je |
| `PUSHOVER_USER_HAVAG` | Első felhasználó User Key-je |
| `PUSHOVER_USER_ENCI` | Második felhasználó User Key-je |

### 3. Kész
A workflow automatikusan fut. Manuális teszteléshez: Actions tab → Pillow Alert → Run workflow.

## Helyszín

Budapest: `47.45804861714617, 19.054431492854786`
