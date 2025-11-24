class NumberShortener:
    _POSTFIXES = [
        '',
        'K',
        'M',
        'B'
    ]

    @classmethod
    def shorten(cls, number: int) -> str:
        power = 0
        while number >= 1_000:
            power += 1
            number //= 1_000

        assert power < len(cls._POSTFIXES)

        return f"{number}{cls._POSTFIXES[power]}"
