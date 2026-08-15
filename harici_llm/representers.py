"""
messagers.py'nin ihtiyac duydugu temsilci (representer) siniflari.

Orijinal messagers.py `arclib.representers` paketinden import ediyordu; bizim
depoda boyle bir paket yok (kullanicinin verdigi 3 dosyadan biri degil). Bu,
"bizim yapacagimiz isle celisen" tek satir grubu: import kaynagini burada,
depo icinde gercekten var olan minimal ama calisan bir uygulamayla
karsiliyoruz. Grid metnini kaidesi bizim tarafimizdan degil, modelin kendisi
tarafindan uretilecek sekilde duz python-listesi / metin bicimine ceviriyor;
herhangi bir bulmaca kurali icermiyor.
"""
from typing import Optional, Tuple

from arc import Example


class GridRepresenter:
    def encode(self, grid) -> str:
        raise NotImplementedError

    def decode(self, text: str):
        raise NotImplementedError


class PythonListGridRepresenter(GridRepresenter):
    def encode(self, grid) -> str:
        return str([[int(c) for c in row] for row in grid])

    def decode(self, text: str):
        import ast
        try:
            parsed = ast.literal_eval(text.strip())
        except (SyntaxError, ValueError):
            return None
        if not isinstance(parsed, list) or not parsed:
            return None
        genislik = len(parsed[0])
        if any(not isinstance(satir, list) or len(satir) != genislik for satir in parsed):
            return None
        return parsed


class TextGridRepresenter(GridRepresenter):
    def encode(self, grid) -> str:
        return "\n".join("".join(str(int(c)) for c in row) for row in grid)

    def decode(self, text: str):
        satirlar = [s for s in text.strip().splitlines() if s.strip()]
        if not satirlar:
            return None
        try:
            grid = [[int(c) for c in satir] for satir in satirlar]
        except ValueError:
            return None
        genislik = len(grid[0])
        if any(len(satir) != genislik for satir in grid):
            return None
        return grid


class CompositeRepresenter(GridRepresenter):
    def __init__(self, connected_component: int = 4, grid_representer: Optional[GridRepresenter] = None):
        self.connected_component = connected_component
        self.grid_representer = grid_representer or PythonListGridRepresenter()

    def encode(self, grid) -> str:
        return self.grid_representer.encode(grid)

    def decode(self, text: str):
        return self.grid_representer.decode(text)


class ExampleRepresenter:
    grid_representer: GridRepresenter

    def encode(self, example: Example, **kwargs) -> Tuple[str, str]:
        raise NotImplementedError


class TextExampleRepresenter(ExampleRepresenter):
    def __init__(self, grid_representer: Optional[GridRepresenter] = None):
        self.grid_representer = grid_representer or TextGridRepresenter()

    def encode(self, example: Example, **kwargs) -> Tuple[str, str]:
        query = f"Input:\n{self.grid_representer.encode(example.input)}\n"
        output = f"Output:\n{self.grid_representer.encode(example.output)}\n"
        return query, output


class DiffExampleRepresenter(ExampleRepresenter):
    def __init__(self, grid_representer: Optional[GridRepresenter] = None, use_output: bool = True):
        self.grid_representer = grid_representer or PythonListGridRepresenter()
        self.use_output = use_output

    def _diff(self, girdi, cikti):
        import numpy as np
        g = np.array(girdi)
        c = np.array(cikti)
        if g.shape != c.shape:
            return c.tolist()
        return (c - g).tolist()

    def encode(self, example: Example, **kwargs) -> Tuple[str, str]:
        girdi_metni = self.grid_representer.encode(example.input)
        fark_metni = self.grid_representer.encode(self._diff(example.input, example.output))
        query = f"Input:\n{girdi_metni}\nDiff:\n"
        if self.use_output:
            cikti_metni = self.grid_representer.encode(example.output)
            output = f"{fark_metni}\nOutput:\n{cikti_metni}\n"
        else:
            output = f"{fark_metni}\n"
        return query, output


class TaskRepresenter:
    def __init__(self, example_representer: Optional[ExampleRepresenter] = None):
        self.example_representer = example_representer or TextExampleRepresenter()


class TextTaskRepresenter(TaskRepresenter):
    pass
