class SchematicAnalyzer:
    def __init__(self, schematic_file):
        from skip import Schematic  # Ensure you have `skip` module installed
        self.schematic_file = schematic_file
        self.schem = Schematic(schematic_file)
        self.connections = []
        self.seen_connections = set()
        print(f"Debug: Initialized analyzer with schematic '{schematic_file}'.")

    def process_schematic(self):
        print("Debug: Processing schematic...")
        print(f"Debug: Found {len(self.schem.bus_alias)} buses and {len(self.schem.symbol)} symbols.")
        for bus in self.schem.bus_alias:
            self.process_bus(bus)
        print("Debug: Finished processing schematic.")

    def process_bus(self, bus):
        bus_name = repr(bus).split()[-1].strip(">'")
        print(f"Debug: Processing bus '{bus_name}'.")
        bus_description, bus_pn = self.get_bus_properties(bus_name)
        bus_members = self.get_bus_members(bus)
        for member in bus_members:
            self.process_bus_member(bus_name, bus_description, bus_pn, member)

    def get_bus_properties(self, bus_name):
        try:
            bus_label = self.schem.label.value_matches(fr"{{{bus_name}}}")[0]
            bus_description = bus_label.property[0].value[1]  # Description
            bus_pn = bus_label.property[1].value[1]           # P/N
            return bus_description, bus_pn
        except Exception as e:
            print(f"Warning: Could not retrieve properties for bus '{bus_name}'. Exception: {e}")
            return "N/A", "N/A"

    def get_bus_members(self, bus):
        try:
            members = bus.members
            print(f"Debug: Found {len(members)} members in bus '{repr(bus)}'.")
            return members
        except Exception as e:
            print(f"Error: Failed to retrieve members for bus '{repr(bus)}'. Exception: {e}")
            return []

    def process_bus_member(self, bus_name, bus_description, bus_pn, member):
        for symbol in self.schem.symbol:
            self.process_symbol(bus_name, bus_description, bus_pn, member, symbol)

    def process_symbol(self, bus_name, bus_description, bus_pn, member, symbol):
        symbol_name = repr(symbol).split()[-1].strip(">'")
        for pin in symbol.pin:
            attached_labels = self.get_pin_labels(pin)
            if member in attached_labels:
                self.find_connections(bus_name, bus_description, bus_pn, member, symbol, pin)

    def get_pin_labels(self, pin):
        labels = []
        try:
            if pin.attached_labels:
                labels = [
                    repr(label.value).split()[-1].strip(">'")
                    for label in pin.attached_labels
                    if label
                ]
        except Exception as e:
            print(f"Warning: Could not process pin labels. Exception: {e}")
        return labels

    def find_connections(self, bus_name, bus_description, bus_pn, member, symbol, pin):
        symbol_name = repr(symbol).split()[-1].strip(">'")
        pin_name = pin.name if pin.name else repr(pin)
        for other_symbol in self.schem.symbol:
            if other_symbol == symbol:
                continue
            self.check_other_symbol(bus_name, bus_description, bus_pn, member, symbol_name, pin_name, other_symbol)

    def check_other_symbol(self, bus_name, bus_description, bus_pn, member, symbol_name, pin_name, other_symbol):
        other_symbol_name = repr(other_symbol).split()[-1].strip(">'")
        for other_pin in other_symbol.pin:
            other_pin_name = other_pin.name if other_pin.name else repr(other_pin)
            other_labels = self.get_pin_labels(other_pin)
            if member in other_labels:
                self.add_connection(bus_name, member, symbol_name, pin_name, other_symbol_name, other_pin_name, bus_description, bus_pn)

    def add_connection(self, bus_name, member, symbol_name, pin_name, other_symbol_name, other_pin_name, bus_description, bus_pn):
        connection = (f"{symbol_name} - {pin_name}", f"{other_symbol_name} - {other_pin_name}")
        if connection not in self.seen_connections and tuple(reversed(connection)) not in self.seen_connections:
            print(f"Debug: Unique connection found: {connection}")
            self.seen_connections.add(connection)
            self.connections.append([
                bus_name, member, connection[0], connection[1], bus_description, bus_pn
            ])
        else:
            print(f"Debug: Duplicate connection skipped: {connection}")

    def print_connections(self):
        header = ["Bus Name", "Wire Name", "To Part - Pin", "From Part - Pin", "Description", "P/N"]
        print(f"{header[0]:<10} {header[1]:<10} {header[2]:<10} {header[3]:<10} {header[4]:<10} {header[5]:<10}")
        print("=" * 70)
        for row in self.connections:
            print(f"{row[0]:<10} {row[1]:<20} {row[2]:<20} {row[3]:<20} {row[4]:<20} {row[5]:<10}")

# Example usage
analyzer = SchematicAnalyzer("abc.kicad_sch")
analyzer.process_schematic()
analyzer.print_connections()



