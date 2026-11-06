import csv

class CLI:
    def __init__(self, input_type: str = "command_line"):
        self.input_type = input_type
        self.params = {}
        if self.input_type == "command_line":
            self.params = self.command_line()

        if self.input_type == 'csv_file':
            self.params = self.csv_file()
    
    def csv_file(self):
        params = {}
        try:
            with open('src/csv_config.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    parameter = row['parameter']
                    value = row['value']
                    params[parameter] = value
        except FileNotFoundError:
            print("File csv_config.csv not found")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка при чтении конфига: {e}")
        return params

    def print_params(self):
        print("Параметры конфигурации:")
        for key in sorted(self.params):
            print(f"  {key}: {self.params[key]}")

if __name__ == "__main__":
    cli = CLI(input_type="csv_file")
    cli.print_params()