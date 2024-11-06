from tabulate import tabulate
import pandas as pd

MAX_INT = 10 ** 9


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
                self.coefficient_matrix[k][j] if self.coefficient_matrix[k][
                                                     j] != MAX_INT else "M"
                for k in range(len(self.supply_vector))
            ]
            representation_dict[f"B{j + 1}"].append(self.demand_vector[j])
        supply_list = []
        supply_list.extend(self.supply_vector)
        supply_list.append(sum(self.supply_vector))
        representation_dict["Supply"] = supply_list
        return pd.DataFrame(representation_dict)

    def __str__(self):
        return tabulate(self.get_table_representation(), headers="keys",
                        tablefmt="fancy_grid")


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
                    # self.table.coefficient_matrix[y][x] = "-"
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
        self.symbols_list = [f"v_{i + 1}"
                             for i in range(len(self.table.demand_vector))]

    def iterate(self):
        delta_table = [[0 for _ in range(len(self.table.supply_vector))]
                       for _ in range(len(self.table.demand_vector))]
        for i in range(len(self.table.demand_vector)):
            for j in range(len(self.table.supply_vector)):
                cost = self.table.coefficient_matrix[j][i]
                row = [self.table.coefficient_matrix[j][k] for k in
                       range(len(self.table.demand_vector))]
                column = [self.table.coefficient_matrix[k][i] for k in
                          range(len(self.table.supply_vector))]
                max_row = max(row)
                max_column = max(column)
                delta_table[i][j] = cost - max_row - max_column

        minimal_coordinates = (0, 0)
        minimum = delta_table[0][0]
        for i in range(1, len(delta_table)):
            for j in range(len(delta_table[i])):
                if delta_table[i][j] < minimum:
                    minimum = delta_table[i][j]
                    minimal_coordinates = (i, j)

        print(f"Minimal coordinates: {minimal_coordinates} with value "
              f"{minimum}")


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
    print(table)
    # print("Method: North West Corner Method")
    # NorthWestCornerMethod(table).solve()
    print("Method: Russell's Approximation Method")
    print("Iteration #1:")
    RussellApproximationMethod(table).iterate()
    print(table)


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
