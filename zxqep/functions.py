"""Provide the primary functions for quantum error propagation in ZX-calculus."""

import pyzx as zx
from pyzx.utils import VertexType
from pyzx.utils import EdgeType
from fractions import Fraction


class ZXQEPNode:
    """A single coordinate point in a discrete error tracking grid.

    Represents a physical point in a ZX circuit. It stores the
    gate occurring at this location and tracks any active Pauli or Clifford phase
    errors residing on the wire immediately before the gate is applied.
    """

    def __init__(self, gate_type="I", partner=None):
        """Initialize a grid node for error tracking.

        Parameters
        ----------
        gate_type : str, optional
            The string identifier of the gate at this coordinate (e.g., "I" (Identity),
            "X" (Pauli X), "Z" (Pauli Z), "H" (Hadamard), "S" (Phase gate),
            "T" (Pi/8 Gate), "CNOT_C" (CNOT gate control node),
            "CNOT_T" (CNOT gate target node), "CZ" (CZ Gate Node)). Defaults to "I".
        partner : int, optional
            The row index of the corresponding control or target qubit if this
            node represents part of a two-qubit gate. Defaults to None.
        """
        self.gate = gate_type  # "I", "X", "Z", "H", "S", "T", "CNOT_C", "CNOT_T", "CZ"
        self.partner = partner  # Target/Control row index for CNOT and CZ

        # Tracks errors (in units of Pi)
        self.x_phase = Fraction(0)  # X Phase (0 = Identity, 1 = Pauli X)
        self.z_phase = Fraction(
            0
        )  # Z Phase (0 = Identity, 1 = Pauli Z, 1/2= S, -1/2 = 3/2 = S)


class ZXQEPGraph:
    """The simulation environment for error propagation. Maps a topological PyZX graph to a strict 2D grid.

    Parses a quantum circuit from standard PyZX representation, allows for the manual
    injection of discrete phase errors, and mathematically propagates those errors
    through the circuit's gates using ZX-calculus rules.
    """

    def __init__(self, g):
        """Initialize the ZX Quantum Error Propagation environment.

        Calculates the global spatial boundaries of the provided PyZX graph, instantiates
        the 2D grid of ZXQEPNodes, and parses the circuit into the grid.

        Parameters
        ----------
        g : pyzx.Graph
            The base PyZX graph to be simulated. Functionality is only designed
            to take input in a circuit-like rectangular form.
        """
        self.original_graph = g

        # Determine the grid boundaries based on PyZX coordinates
        rows = [g.qubit(v) for v in g.vertices()]
        cols = [g.row(v) for v in g.vertices()]

        self.row_min, self.row_max = min(rows), max(rows)
        self.col_min, self.col_max = min(cols), max(cols)

        self.num_rows = (self.row_max - self.row_min) + 1
        self.num_cols = (self.col_max - self.col_min) + 1

        # Initialize the internal tracking grid
        self.grid = [
            [ZXQEPNode() for _ in range(self.num_cols)] for _ in range(self.num_rows)
        ]

        # Parse the graph into the grid
        self._extract_schedule()

    def _extract_schedule(self):
        """Helper Function to parse the PyZX graph into the rigid 2D spacetime simulation grid.

        Iterates through the mapped coordinate system. If a PyZX vertex exists at a
        given coordinate, it checks the VertexType and phase to classify the standard
        gate operations. It also scans adjacent vertices in the same column to identify,
        classify, and link two-qubit gates (CNOT and CZ).
        """
        g = self.original_graph
        coord_map = {(g.qubit(v), g.row(v)): v for v in g.vertices()}

        for r in range(self.num_rows):
            for c in range(self.num_cols):
                real_q = r + self.row_min
                real_r = c + self.col_min

                v = coord_map.get((real_q, real_r))
                if v is None:
                    continue

                v_type = g.type(v)
                phase = g.phase(v)

                if v_type == VertexType.H_BOX:
                    self.grid[r][c].gate = "H"
                elif v_type == VertexType.X:
                    if phase == Fraction(1, 1) or phase == Fraction(-1, 1):
                        self.grid[r][c].gate = "X"
                elif v_type == VertexType.Z:
                    if phase == Fraction(1, 1) or phase == Fraction(-1, 1):
                        self.grid[r][c].gate = "Z"
                    elif phase == Fraction(1, 2):
                        self.grid[r][c].gate = "S"
                    elif phase == Fraction(-1, 2) or phase == Fraction(3, 2):
                        self.grid[r][c].gate = "S_DAG"
                    elif phase == Fraction(1, 4):
                        self.grid[r][c].gate = "T"
                    elif phase == Fraction(-1, 4) or phase == Fraction(7, 4):
                        self.grid[r][c].gate = "T_DAG"

                    # Detect Two-Qubit Gates
                    for neighbor in g.neighbors(v):
                        if g.row(neighbor) == real_r:
                            # Detect CNOT (Z connected to X via simple edge)
                            if (
                                g.type(neighbor) == VertexType.X
                                and g.edge_type(g.edge(v, neighbor)) == EdgeType.SIMPLE
                            ):
                                self.grid[r][c].gate = "CNOT_C"
                                target_r = g.qubit(neighbor) - self.row_min
                                self.grid[r][c].partner = target_r
                                self.grid[target_r][c].gate = "CNOT_T"
                                self.grid[target_r][c].partner = r
                            # Detect CZ (Z connected to Z via Hadamard edge)
                            elif (
                                g.type(neighbor) == VertexType.Z
                                and g.edge_type(g.edge(v, neighbor))
                                == EdgeType.HADAMARD
                            ):
                                if (
                                    self.grid[r][c].gate == "I"
                                ):  # partner hasn't been assigned yet
                                    self.grid[r][c].gate = "CZ"
                                    target_r = g.qubit(neighbor) - self.row_min
                                    self.grid[r][c].partner = target_r
                                    self.grid[target_r][c].gate = "CZ"
                                    self.grid[target_r][c].partner = r

    def inject_error(self, row, col, err_type="I", fraction_val=1):
        """Inject a discrete phase error into the wire just before a specified gate.

        Parameters
        ----------
        row : int
            The relative grid row (qubit index) where the error occurs.
        col : int
            The relative grid column (time-step) right before where the error occurs. Should be 0 >
        err_type : str
            The type of Pauli error to inject ("X", "Y", or "Z").
        fraction_val : int, float, or Fraction
            The magnitude of the error phase in units of pi.

        Examples
        --------
        >>> error_graph.inject_error(row=0, col=2, err_type="X", fraction_val=1)
        """
        if col <= 0:
            raise ValueError(
                "Error injection failed: Cannot inject errors before the input boundary."
            )

        if err_type == "X":
            self.grid[row][col].x_phase += Fraction(fraction_val)
        elif err_type == "Z":
            self.grid[row][col].z_phase += Fraction(fraction_val)
        elif err_type == "Y":
            self.grid[row][col].x_phase += Fraction(fraction_val)
            self.grid[row][col].z_phase += Fraction(fraction_val)

        self.grid[row][col].x_phase %= 2
        self.grid[row][col].z_phase %= 2

    def propagate_to_end(self, print_errors=True):
        """Propagate injected errors forward through the circuit to the final boundary.

        Parses through the ZXQEPGraph object's grid, applying standard ZX calculus
        rules to transform and push errors through gates

        Note: Currently, there is only functionality for simulating Clifford errors.
        If the propagation would produce a non-Clifford error, propagation ends and
        returns False.

        Parameters
        ----------
        print_errors : bool, optional
            If True, prints a summary of all residual errors on the logical qubits
            at the end of the circuit. Defaults to True.

        Returns
        -------
        bool
            True if propagation completed successfully through the entire circuit.
            False if an un-propagatable (non-Clifford) error would have been produced
        """
        for t in range(self.num_cols - 1):
            for r in range(self.num_rows):
                current_node = self.grid[r][t]
                next_node = self.grid[r][t + 1]

                x_err = current_node.x_phase
                z_err = current_node.z_phase

                if x_err % 2 == 0 and z_err % 2 == 0:
                    continue

                current_node.x_phase = Fraction(0)
                current_node.z_phase = Fraction(0)

                gate = current_node.gate

                # Propgagation rules

                if gate == "X":
                    z_err = -z_err

                elif gate == "Z":
                    x_err = -x_err

                elif gate == "H":
                    x_err, z_err = z_err, x_err

                elif gate in ["S", "T", "S_DAG", "T_DAG"]:
                    if x_err % 1 != 0:
                        print(
                            "This error is too complicated, and can not be propagated"
                        )
                        return False

                    if x_err != 0:
                        if gate == "S":
                            z_err += Fraction(-1, 1) * x_err  # Spawns Z(-pi)
                        elif gate == "T":
                            z_err += Fraction(-1, 2) * x_err  # Spawns S_dag
                        elif gate == "S_DAG":
                            z_err += Fraction(1, 1) * x_err  # Spawns Z(pi)
                        elif gate == "T_DAG":
                            z_err += Fraction(1, 2) * x_err  # Spawns S

                elif gate == "CNOT_C":
                    if x_err % 1 != 0:
                        print(
                            "This error is too complicated, and can not be propagated"
                        )
                        return False

                    if x_err != 0:
                        target = current_node.partner
                        self.grid[target][t + 1].x_phase += x_err

                elif gate == "CNOT_T":
                    if z_err % 1 != 0:
                        print(
                            "This error is too complicated, and can not be propagated"
                        )
                        return False

                    if z_err != 0:
                        control = current_node.partner
                        self.grid[control][t + 1].z_phase += z_err

                elif gate == "CZ":
                    if x_err % 1 != 0:
                        print(
                            "This error is too complicated, and can not be propagated"
                        )
                        return False

                    # A Pauli X error on either qubit copies as a Z error to the partner
                    # Z errors passes through without spreading
                    if x_err != 0:
                        partner = current_node.partner
                        self.grid[partner][t + 1].z_phase += x_err

                next_node.x_phase += x_err
                next_node.z_phase += z_err

                next_node.x_phase %= 2
                next_node.z_phase %= 2

        # --- FINAL ERROR PARSING AND PRINTING ---
        if print_errors:
            error_found = False
            final_col = self.num_cols - 1

            # Check the phase state of every qubit in the final column
            for r in range(self.num_rows):
                final_node = self.grid[r][final_col]
                x_final = final_node.x_phase
                z_final = final_node.z_phase

                # Only print if an error exists
                if x_final != 0 or z_final != 0:
                    print(
                        f"    Qubit-{r + 1}: x-error = {x_final}, z-error = {z_final}"
                    )
                    error_found = True

            if not error_found:
                print("No propagated errors.")
        else:
            # Only print the baseline success if detailed printing is off
            print("Propagation complete.")

        return True

    def to_pyzx_graph(self):
        """Generate a PyZX graph visualizing current errors as phase spiders.

        Clones the original PyZX graph, standardizes the boundary alignments, and
        inserts current errors from the ZXQEP object's error tracking grid
        directly onto the graphical wires.

        Returns
        -------
        pyzx.Graph
            A new, modified PyZX graph containing visual error nodes.
        """
        g_vis = self.original_graph.clone()

        # Determine circuit bounds and align boundaries globally (hardcoded in for simplicity)
        boundaries = []
        max_gate_col = 0
        min_gate_col = 10000

        # Scan the graph to find where the actual gates start and end
        for v in g_vis.vertices():
            if len(list(g_vis.neighbors(v))) == 1:
                boundaries.append(v)
            else:
                col = g_vis.row(v)
                if col > max_gate_col:
                    max_gate_col = col
                if col < min_gate_col:
                    min_gate_col = col

        if min_gate_col == 10000:
            min_gate_col = 0

        # Enforce perfectly rectangular boundaries
        for v_bnd in boundaries:
            neighbor = list(g_vis.neighbors(v_bnd))[0]
            if g_vis.row(v_bnd) < g_vis.row(neighbor):
                # Input boundary: push everyone to the exact same left column
                g_vis.set_row(v_bnd, min_gate_col - 2)
            else:
                # Output boundary: push everyone to the exact same right column
                g_vis.set_row(v_bnd, max_gate_col + 3)

        # Group all vertices by their physical qubit (grid rows)
        qubit_vertices = {}
        for v in g_vis.vertices():
            q = g_vis.qubit(v)
            if q not in qubit_vertices:
                qubit_vertices[q] = []
            qubit_vertices[q].append(v)

        for q in qubit_vertices:
            qubit_vertices[q].sort(key=lambda x: g_vis.row(x))

        # Iterate over the ENTIRE simulation grid
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                target_node = self.grid[r][c]

                if target_node.x_phase == 0 and target_node.z_phase == 0:
                    continue

                real_q = r + self.row_min

                if real_q not in qubit_vertices or len(qubit_vertices[real_q]) < 2:
                    continue

                verts = qubit_vertices[real_q]

                # Find the exact horizontal edge (wire) using PRE-GATE alignment
                v_left = None
                v_right = None

                for i in range(len(verts) - 1):
                    if g_vis.row(verts[i]) < c and g_vis.row(verts[i + 1]) >= c:
                        if g_vis.connected(verts[i], verts[i + 1]):
                            v_left = verts[i]
                            v_right = verts[i + 1]
                            break

                # If error is before the very first gate
                if v_left is None and c <= g_vis.row(verts[0]):
                    for i in range(len(verts) - 1):
                        if g_vis.connected(verts[i], verts[i + 1]):
                            v_left = verts[i]
                            v_right = verts[i + 1]
                            break

                # If error is after the very last gate
                if v_left is None:
                    for i in range(len(verts) - 2, -1, -1):
                        if g_vis.connected(verts[i], verts[i + 1]):
                            v_left = verts[i]
                            v_right = verts[i + 1]
                            break

                # Perform the surgery with Strict Alignment Logic
                if v_left is not None and v_right is not None:
                    original_edge_type = g_vis.edge_type(g_vis.edge(v_left, v_right))
                    g_vis.remove_edge(g_vis.edge(v_left, v_right))

                    curr_v = v_left
                    curr_edge_type = original_edge_type

                    left_col = g_vis.row(v_left)
                    right_col = g_vis.row(v_right)

                    has_x = target_node.x_phase != 0
                    has_z = target_node.z_phase != 0

                    # --- Uniform Output Alignment ---
                    if g_vis.type(v_right) == 0:
                        if has_x and has_z:
                            pos_x = max_gate_col + 1.0
                            pos_z = max_gate_col + 2.0
                        elif has_x:
                            pos_x = max_gate_col + 1.5
                        elif has_z:
                            pos_z = max_gate_col + 1.5

                    # --- Mid-Circuit Unpropagated Errors ---
                    else:
                        gap = right_col - left_col
                        if has_x and has_z:
                            pos_x = left_col + (gap * 0.33)
                            pos_z = left_col + (gap * 0.66)
                        elif has_x:
                            pos_x = left_col + (gap * 0.5)
                        elif has_z:
                            pos_z = left_col + (gap * 0.5)

                    # Inject the Spiders
                    if has_x:
                        v_x = g_vis.add_vertex(
                            VertexType.X,
                            qubit=real_q,
                            row=pos_x,
                            phase=target_node.x_phase,
                        )
                        g_vis.add_edge(g_vis.edge(curr_v, v_x), edgetype=curr_edge_type)
                        curr_v = v_x
                        curr_edge_type = EdgeType.SIMPLE

                    if has_z:
                        v_z = g_vis.add_vertex(
                            VertexType.Z,
                            qubit=real_q,
                            row=pos_z,
                            phase=target_node.z_phase,
                        )
                        g_vis.add_edge(g_vis.edge(curr_v, v_z), edgetype=curr_edge_type)
                        curr_v = v_z
                        curr_edge_type = EdgeType.SIMPLE

                    # Reconnect to the rest of the circuit
                    g_vis.add_edge(g_vis.edge(curr_v, v_right), edgetype=curr_edge_type)

        return g_vis

    def draw(self):
        """Render the visual representation of the quantum circuit with active errors.

        Converts the current ZXQEPGraph object into a PyZX graph using `to_pyzx_graph`
        and plots it using PyZX's draw function.
        """
        zx.draw(self.to_pyzx_graph())
