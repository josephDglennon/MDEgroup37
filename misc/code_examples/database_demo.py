import sqlite3

class employee:

    def __init__(self, first, last, pay):
        self.first = first
        self.last = last
        self.pay = pay

    @property
    def email(self):
        return '{}.{}@email.com'.format(self.first, self.last)
    
    @property
    def fullname(self):
        return '{} {}'.format(self.first, self.last)
    
    def __repr__(self):
        return "Employee('{}', '{}', {})".format(self.first, self.last, self.pay)
    
def main():
    
    conn = sqlite3.connect('./demo.db')
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            first text,
            last test,
            pay integer
        );
    """)

    #c.execute("INSERT INTO employees VALUES ('Josh', 'Barenson', 900)")
    #c.execute("INSERT INTO employees VALUES ('Jacob', 'Barenson', 800)")

    c.execute("SELECT * FROM employees WHERE last='Barenson'")

    emp1 = employee('Jane', 'Doe', 420)
    emp2 = employee('John', 'Doe', 690)

    #c.execute("INSERT INTO employees VALUES (?, ?, ?)", (emp1.first, emp1.last, emp1.pay))
    #c.execute("INSERT INTO employees VALUES (?, ?, ?)", (emp2.first, emp2.last, emp2.pay))

    print(c.fetchall())

    conn.commit()

    conn.close()

if __name__ == '__main__':
    main()