from textual.widgets import Static

class MiniProgressBar(Static):
    PROGRESS_STYLE = ("█", " ")
    BAR_COLORS = (
        (lambda x: x < .5, "green"),
        (lambda x: x < .8, "yellow"),
        (lambda x: True, "red")
    )

    def __init__(self,  bar_name:str, **kwargs):
        super().__init__(**kwargs)

        self.bar_name = bar_name

    def update_progress(self, value: float=.25) -> None:
        width = int(self.size.width) - len(f'{self.bar_name} : ') - 1
        filled = int(width * value)
        bar = self.PROGRESS_STYLE[0] * filled + self.PROGRESS_STYLE[1] * (width - filled)

        self.update(f"{self.bar_name} : {bar}")

        for limits in self.BAR_COLORS:
            if limits[0](value):
                self.styles.color = limits[1]
                break