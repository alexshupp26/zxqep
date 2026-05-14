"""
Unit and regression test for the zxqep package.
"""

# Import package, test suite, and other packages as needed
import sys
import pytest
import pyzx as zx
import zxqep as ep

# Import test that came with CookieCutter
def test_zxqep_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "zxqep" in sys.modules

@pytest.mark.parametrize(
    "gate_type, gate_phase, injected_error, expected_output, ",
    [
        # --- Z-Gate (Green spider, phase = 1) ---
        (1, 1.0, 'X', 'Qubit-1: x-error = 1, z-error = 0'), 
        (1, 1.0, 'Z', 'Qubit-1: x-error = 0, z-error = 1'), 
        
        # --- X-Gate (Red spider, phase = 1) ---
        (2, 1.0, 'X', 'Qubit-1: x-error = 1, z-error = 0'), 
        (2, 1.0, 'Z', 'Qubit-1: x-error = 0, z-error = 1'), 
        
        # --- S-Gate (Green spider, phase = 1/2) ---
        (1, 0.5, 'X', 'Qubit-1: x-error = 1, z-error = 1'), 
        (1, 0.5, 'Z', 'Qubit-1: x-error = 0, z-error = 1'), 
        
        # --- H-Gate (H-Box, Type = 3) ---
        (3, 0.0, 'X', 'Qubit-1: x-error = 0, z-error = 1'), 
        (3, 0.0, 'Z', 'Qubit-1: x-error = 1, z-error = 0'),

        # --- T-Gate (Green spider, phase = 1/4)  ---
        (1, 0.25, 'X', 'Qubit-1: x-error = 1, z-error = 3/2'), 
        (1, 0.25, 'Z', 'Qubit-1: x-error = 0, z-error = 1'),
    ]
)

# Testing error propogation rules for single-qubit gates
def test_single_qubit_error_propagation_rules(capsys, gate_type, gate_phase, injected_error, expected_output):
    """
    Tests that Pauli errors propagate correctly through specific single-qubit gates.
    """
    # Create PyZX Graph 
    g = zx.Graph()
    
    # Add Input 
    v00 = g.add_vertex(1, 0, 0)
    
    # Gate (Starts as an Pauli-X)
    v01 = g.add_vertex(gate_type, 0, 1, gate_phase)
    
    # Outputs (Col 2)
    v02 = g.add_vertex(0, 0, 2)
    
    # Edges
    g.add_edges([(v00, v01), (v01, v02)])
    
    # Create your ZXQEPGraph object
    g_error = ep.ZXQEPGraph(g)
    
    # Inject your starting error 
    g_error.inject_error(row=0, col=1, err_type=injected_error)
    
    # Propagate the error
    g_error.propagate_to_end()
    
    # Read the actual output
    captured = capsys.readouterr()
    
    # Sse .strip() removes trailing newlines.
    actual_output = captured.out.strip()
    
    # Assert the expected string is inside the printed output
    assert expected_output == actual_output, \
        f"Failed on Gate {gate_type} (Phase {gate_phase}). Expected '{expected_output}' in output, got '{actual_output}'"



# Testing error propogation rules for a CNOT gate
@pytest.mark.parametrize(
    "injected_error_CNOT, location_of_error_CNOT, expected_output_CNOT, ",
    [
        # --- Pauli-X Error (Red spider, phase = 1) ---
        ('X', 0, 'Qubit-1: x-error = 1, z-error = 0\n    Qubit-2: x-error = 1, z-error = 0'), 
        ('X', 1, 'Qubit-2: x-error = 1, z-error = 0'), 

        # --- Pauli-Z Error (Green spider, phase = 1) ---
        ('Z', 0, 'Qubit-1: x-error = 0, z-error = 1'), 
        ('Z', 1, 'Qubit-1: x-error = 0, z-error = 1\n    Qubit-2: x-error = 0, z-error = 1'), 
    ]
)


# Testing Error Propagation rules for the CNOT gate
def test_CNOT_error_propagation_rules(capsys, injected_error_CNOT, location_of_error_CNOT, expected_output_CNOT):
    """
    Tests that Pauli errors propagate correctly through a CNOT gate.
    """
    # Create PyZX Graph 
    g = zx.Graph()
    
    # Add Inputa
    v00 = g.add_vertex(1, 0, 0)
    v10 = g.add_vertex(1, 1, 0)
    
    # CNOT12
    v01 = g.add_vertex(1, 0, 1)
    v11 = g.add_vertex(2, 1, 1)
    g.add_edge((v01,v11))
    
    # Outputs 
    v02 = g.add_vertex(0, 0, 2)
    v12 = g.add_vertex(0, 1, 2)

    # Edges
    g.add_edges([(v00, v01), (v01, v02)])
    g.add_edges([(v10, v11), (v11, v12)])

    # Create your ZXQEPGraph object
    g_error = ep.ZXQEPGraph(g)
    
    # Inject your starting error 
    g_error.inject_error(row=location_of_error_CNOT, col=1, err_type=injected_error_CNOT)
    
    # Propagate the error
    g_error.propagate_to_end()
    
    # Read the actual output
    captured = capsys.readouterr()
    
    # Sse .strip() removes trailing newlines.
    actual_output = captured.out.strip()
    
    # Assert the expected string is inside the printed output
    assert expected_output_CNOT == actual_output, \
        f"Failed on Error {injected_error_CNOT} on qubit {location_of_error_CNOT + 1}. Expected '{expected_output_CNOT}' in output, got '{expected_output_CNOT}'"
    
# Testing error propogation rules for a CZ gate
@pytest.mark.parametrize(
    "injected_error_CZ, location_of_error_CZ, expected_output_CZ, ",
    [
        # --- Pauli-X Error (Red spider, phase = 1) ---
        ('X', 0, 'Qubit-1: x-error = 1, z-error = 0\n    Qubit-2: x-error = 0, z-error = 1'), 
        ('X', 1, 'Qubit-1: x-error = 0, z-error = 1\n    Qubit-2: x-error = 1, z-error = 0'), 

        # --- Pauli-Z Error (Green spider, phase = 1) ---
        ('Z', 0, 'Qubit-1: x-error = 0, z-error = 1'), 
        ('Z', 1, 'Qubit-2: x-error = 0, z-error = 1'), 
        
    ]
)


# Testing Error Propagation rules for the CZ gate
def test_CNOT_error_propagation_rules(capsys, injected_error_CZ, location_of_error_CZ, expected_output_CZ):
    """
    Tests that Pauli errors propagate correctly through a CZ gate
    """
    # Create PyZX Graph 
    g = zx.Graph()
    
    # Add Inputa
    v00 = g.add_vertex(1, 0, 0)
    v10 = g.add_vertex(1, 1, 0)
    
    # CNOT12
    v01 = g.add_vertex(1, 0, 1)
    v11 = g.add_vertex(1, 1, 1)
    g.add_edge((v01,v11),2)
    
    # Outputs 
    v02 = g.add_vertex(0, 0, 2)
    v12 = g.add_vertex(0, 1, 2)

    # Edges
    g.add_edges([(v00, v01), (v01, v02)])
    g.add_edges([(v10, v11), (v11, v12)])

    # Create your ZXQEPGraph object
    g_error = ep.ZXQEPGraph(g)
    
    # Inject your starting error 
    g_error.inject_error(row=location_of_error_CZ, col=1, err_type=injected_error_CZ)
    
    # Propagate the error
    g_error.propagate_to_end()
    
    # Read the actual output
    captured = capsys.readouterr()
    
    # Sse .strip() removes trailing newlines.
    actual_output = captured.out.strip()
    
    # Assert the expected string is inside the printed output
    assert expected_output_CZ == actual_output, \
        f"Failed on Error {injected_error_CZ} on qubit {location_of_error_CZ + 1}. Expected '{expected_output_CZ}' in output, got '{actual_output}'"



