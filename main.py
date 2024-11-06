from tabulate import tabulate
import pandas as pd


class Table:
    def __init__(self, supply_vector, coefficient_matrix, demand_vector):
        self.supply_vector = supply_vector
        self.coefficient_matrix = coefficient_matrix
        self.demand_vector = demand_vector

    def get_table_representation(self):
        representation_dict = {
            "Source": [f"A{i + 1}"
                       for i in range(len(self.supply_vector))]
        }
        representation_dict["Source"].append("Demand")
        for j in range(len(self.demand_vector)):
            representation_dict[f"B{j + 1}"] = [
                self.coefficient_matrix[k][j]
                for k in range(len(self.supply_vector))
            ]
            representation_dict[f"B{j + 1}"].append(self.demand_vector[j])
        representation_dict["Supply"] = self.supply_vector
        representation_dict["Supply"].append(sum(self.supply_vector))
        return pd.DataFrame(representation_dict)


class NorthWestCornerMethod:
    def __init__(self, table):
        self.table = table

    def solve(self):
        total_distribution_cost = 0
        for x in range(len(self.table.demand_vector)):
            for y in range(len(self.table.supply_vector)):
                current_demand_element = self.table.demand_vector[x]
                current_supply_element = self.table.supply_vector[y]
                current_table_element = self.table.coefficient_matrix[y][x]

                if current_demand_element == 0 or current_supply_element == 0:
                    self.table.coefficient_matrix[y][x] = "-"
                    continue

                minimal_demand_supply = min(current_demand_element,
                                            current_supply_element)
                total_distribution_cost += (minimal_demand_supply *
                                            current_table_element)

                self.table.coefficient_matrix[y][x] = str(
                    self.table.coefficient_matrix[y][
                        x]) + f"({minimal_demand_supply})"
                self.table.demand_vector[x] -= minimal_demand_supply
                self.table.supply_vector[y] -= minimal_demand_supply
        if sum(self.table.demand_vector) != sum(self.table.supply_vector):
            raise BalanceError
        print(f"Total distribution cost: {total_distribution_cost}")


class VogelApproximationMethod:
    def __init__(self, table):
        self.table = table

    def solve(self):
        pass


class RussellApproximationMethod:
    def __init__(self, table):
        self.table = table

    def solve(self):
        pass


def form_table():
    supply_vector = list(map(int, input().split()))
    coefficient_matrix = []
    for _ in range(len(supply_vector)):
        coefficient_matrix.append(list(map(int, input().split())))
    demand_vector = list(map(int, input().split()))
    if sum(supply_vector) != sum(demand_vector):
        raise ApplicabilityError
    return Table(supply_vector, coefficient_matrix, demand_vector)


def main():
    table = form_table()
    NorthWestCornerMethod(table).solve()
    print(tabulate(table.get_table_representation(), headers="keys",
                   tablefmt="fancy_grid"))


class BalanceError(Exception):
    pass


class ApplicabilityError(Exception):
    pass


if __name__ == "__main__":
    try:
        main()
    except ApplicabilityError:
        print("The method is not applicable!")
    except BalanceError:
        print("The problem is not balanced!")
