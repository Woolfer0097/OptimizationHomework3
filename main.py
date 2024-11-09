from tabulate import tabulate
import pandas as pd
import copy

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
                    self.table.coefficient_matrix[y][x] = 0
                    continue

                minimal_demand_supply = min(current_demand_element,
                                            current_supply_element)
                total_distribution_cost += (minimal_demand_supply *
                                            current_table_element)

                self.table.coefficient_matrix[y][x] = minimal_demand_supply
                self.table.demand_vector[x] -= minimal_demand_supply
                self.table.supply_vector[y] -= minimal_demand_supply
        if sum(self.table.demand_vector) != sum(self.table.supply_vector):
            raise BalanceError
        print(f"Total distribution cost: {total_distribution_cost}")
        print(
            f"Vector x0: {', '.join(map(str, self.table.coefficient_matrix))}")


class VogelApproximationMethod:
    def __init__(self, table):
        self.table = table

    def solve(self):
        table_copy = copy.deepcopy(self.table)
        table_cost = [[0] * len(table_copy.demand_vector) for _ in
                      range(len(table_copy.supply_vector))]

        while max(table_copy.demand_vector) > 0 and max(
                table_copy.supply_vector) > 0:
            by_row = []
            by_column = []

            for i, row in enumerate(table_copy.coefficient_matrix):
                costs = [c for j, c in enumerate(row) if
                         table_copy.demand_vector[j] > 0 and c != -1]
                if len(costs) > 1:
                    by_row.append(sorted(costs)[1] - sorted(costs)[0])
                elif costs:
                    by_row.append(costs[0])
                else:
                    by_row.append(-1)

            for j in range(len(table_copy.demand_vector)):
                costs = [table_copy.coefficient_matrix[i][j] for i in
                         range(len(table_copy.supply_vector)) if
                         table_copy.supply_vector[i] > 0 and
                         table_copy.coefficient_matrix[i][j] != -1]
                if len(costs) > 1:
                    by_column.append(sorted(costs)[1] - sorted(costs)[0])
                elif costs:
                    by_column.append(costs[0])
                else:
                    by_column.append(-1)

            max_by_row_ = max(by_row) if any(x >= 0 for x in by_row) else -1
            max_by_column = max(by_column) if any(
                x >= 0 for x in by_column) else -1

            if max_by_row_ >= max_by_column:
                i_min = by_row.index(max_by_row_)
                j_min = min((j for j in range(len(table_copy.demand_vector)) if
                             table_copy.demand_vector[j] > 0),
                            key=lambda j: table_copy.coefficient_matrix[i_min][
                                j])
            else:
                j_min = by_column.index(max_by_column)
                i_min = min((i for i in range(len(table_copy.supply_vector)) if
                             table_copy.supply_vector[i] > 0),
                            key=lambda i: table_copy.coefficient_matrix[i][
                                j_min])

            value = min(table_copy.supply_vector[i_min],
                        table_copy.demand_vector[j_min])
            table_cost[i_min][j_min] = value
            table_copy.supply_vector[i_min] -= value
            table_copy.demand_vector[j_min] -= value
            table_copy.coefficient_matrix[i_min][j_min] = -1

            if table_copy.supply_vector[i_min] == 0:
                for j in range(len(table_copy.demand_vector)):
                    table_copy.coefficient_matrix[i_min][j] = -1

            if table_copy.demand_vector[j_min] == 0:
                for i in range(len(table_copy.supply_vector)):
                    table_copy.coefficient_matrix[i][j_min] = -1

        total_cost = sum(
            table_cost[i][j] * self.table.coefficient_matrix[i][j]
            for i in range(len(self.table.supply_vector))
            for j in range(len(self.table.demand_vector))
            if table_cost[i][j] > 0
        )
        print(f"Total distribution cost: {total_cost}")

        print("Final cost vector: ")
        print(', '.join(map(str, [table_cost[i] for i in range(3)])))


class RussellApproximationMethod:
    def __init__(self, table):
        self.table = table
        self.total_distribution_cost = 0

    def iterate(self):
        for i in range(10):
            delta_table = [[0 for _ in range(len(self.table.supply_vector))]
                           for _ in range(len(self.table.demand_vector))]

            # print supply vector
            print(self.table.supply_vector)

            # print demand vector
            print(self.table.demand_vector)

            # print coefficient matrix
            for row in self.table.coefficient_matrix:
                print(row)

            # calculate delta table
            for i in range(len(self.table.demand_vector)):
                for j in range(len(self.table.supply_vector)):
                    cost = self.table.coefficient_matrix[j][i]
                    row = [self.table.coefficient_matrix[j][k] for k in
                           range(len(self.table.demand_vector))]
                    column = [self.table.coefficient_matrix[k][i] for k in
                              range(len(self.table.supply_vector))]
                    max_row = max(row)
                    max_column = max(column)
                    print(f"max row: {max_row}\nmax column: {max_column}")
                    delta_table[i][j] = cost - max_row - max_column

            minimal_coordinates = (0, 0)
            minimum = delta_table[0][0]
            for i in range(1, len(delta_table)):
                for j in range(len(delta_table[i])):
                    if delta_table[i][j] < minimum:
                        minimum = delta_table[i][j]
                        minimal_coordinates = (i, j)

            # print delta table
            for row in delta_table:
                print(row)

            print(f"Minimal coordinates: {minimal_coordinates} with value "
                  f"{minimum}")
            x, y = minimal_coordinates
            current_demand_element = self.table.demand_vector[x]
            current_supply_element = self.table.supply_vector[y]
            current_table_element = self.table.coefficient_matrix[y][x]

            if current_demand_element == 0 or current_supply_element == 0:
                self.table.coefficient_matrix[y][x] = 0
                continue

            if current_demand_element == 0 and current_supply_element == 0:
                return

            minimal_demand_supply = min(current_demand_element,
                                        current_supply_element)
            self.total_distribution_cost += (minimal_demand_supply *
                                             current_table_element)

            self.table.coefficient_matrix[y][x] = minimal_demand_supply
            self.table.demand_vector[x] -= minimal_demand_supply
            self.table.supply_vector[y] -= minimal_demand_supply

            if sum(self.table.demand_vector) != sum(self.table.supply_vector):
                raise BalanceError

    def solve(self):
        self.iterate()
        print(f"Total distribution cost: {self.total_distribution_cost}")
        print(
            f"Vector x0: {', '.join(map(str, self.table.coefficient_matrix))}")


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
    print("Initial table:\n")
    print(table)
    northwest_table = copy.deepcopy(table)
    print(
        "================\nMethod: North West Corner Method\n================")
    NorthWestCornerMethod(northwest_table).solve()
    vogel_table = copy.deepcopy(table)

    print("\n\n================\nMethod: Vogel's Method\n================")
    VogelApproximationMethod(vogel_table).solve()

    russell_table = copy.deepcopy(table)
    print(
        "\n\n================\nMethod: Russell's "
        "Approximation Method\n================")
    RussellApproximationMethod(russell_table).solve()


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
