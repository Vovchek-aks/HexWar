class NumberShortener:
    _POSTFIXES = [
        '',
        'K',
        'M',
        'B',
        "T",
        "Q"
    ]

    @classmethod
    def shorten(cls, number: int) -> str:
        sign = 1
        if number < 0:
            sign = -1
            number = abs(number)

        power = 0
        while number >= 1_000:
            power += 1
            number /= 1_000

        assert power < len(cls._POSTFIXES)

        return f"{sign * number:.1f}{cls._POSTFIXES[power]}"
