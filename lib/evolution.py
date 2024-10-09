import cmath


from qiskit import QuantumCircuit


def get_bell_evolution_circ(operator, dt, *, barrier=False):
    meas_circ_dict = {}
    coeffs_dict = {}
    num_qubits = operator.num_qubits
    circ = QuantumCircuit(num_qubits)

    for term_op, coeff in zip(operator.op_list, operator.coeffs):
        # Listing qubits where term_op acts on non-trivially.
        qubits_s01 = []
        qubits_s10 = []
        qubits_s00 = []
        qubits_s11 = []

        for i, op in enumerate(reversed(term_op)): # The "term op" is "reversed" to fit the endian to that of qiskit.
            if op == 'm': 
                qubits_s01.append(i)
            elif op == 'p':
                qubits_s10.append(i)
            elif op == 'z':
                qubits_s00.append(i)
            elif op == 'o':
                qubits_s11.append(i)
        
        # Since we assume that the operator is symmetric matrix, 
        # we only focus on the term where the left most non-trivial operator is s01
        # to construct the circuit.
        if len(qubits_s01) > 0:
            if len(qubits_s10) == 0 or qubits_s01[-1] > qubits_s10[-1]:
                
                q_controls = []
                
                # Rotating basis to the Bell basis
                for i in reversed(qubits_s01[:-1]):
                    circ.cx(qubits_s01[-1], i)
                    circ.x(i) # flipping the qubit for applying the mcrz gate controlled by the 0 state.
                    q_controls.append(circ.qubits[i])
                for i in reversed(qubits_s10):
                    circ.cx(qubits_s01[-1], i)
                    q_controls.append(circ.qubits[i])

                lam = cmath.phase(coeff)
                gam = abs(coeff)

                circ.p(lam, qubits_s01[-1])
                circ.h(qubits_s01[-1])

                if barrier:
                    circ.barrier()
                
                # rotation
                if len(q_controls) > 0:
                    circ.mcrz(2*dt*gam, q_controls, circ.qubits[qubits_s01[-1]])
                else:
                    circ.rz(2*dt*gam, circ.qubits[qubits_s01[-1]])

                if barrier:
                    circ.barrier()

                # uncomputation
                circ.h(qubits_s01[-1])
                circ.p(-lam, qubits_s01[-1])
                for i in qubits_s10:
                    circ.cx(qubits_s01[-1], i)
                for i in qubits_s01[:-1]:
                    circ.x(i) # flipping the qubit for applying the mcrz gate controlled by the 0 state.
                    circ.cx(qubits_s01[-1], i)
                
                if barrier:
                    circ.barrier()
                    circ.barrier()

    return circ