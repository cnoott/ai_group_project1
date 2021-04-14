    def print_QTable(self):
        print('Q TABLE WITHOUT BLOCK:')
        for x in range(self.world.height):
            for y in range(self.world.width):
                print(f'({x},{y}): ', end='')
                for k, v in self.q_table_no_block[x, y].items():
                    v = round(v, 4)
                    print(f'{k}: {v:.4f}','\t', end='', sep='')
                print()
        print('\nQ TABLE WITH BLOCK:')
        for x in range(self.world.height):
            for y in range(self.world.width):
                print(f'({x},{y}): ', end='')
                for k, v in self.q_table_block[x, y].items():
                    v = round(v, 4)
                    print(f'{k}: {v:.4f}','\t', end='', sep='')
                print()