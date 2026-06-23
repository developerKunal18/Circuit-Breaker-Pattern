from flask import Flask, jsonify
import random
import time

app = Flask(__name__)

# Circuit Breaker State
circuit_state = "CLOSED"

failure_count = 0

FAILURE_THRESHOLD = 3

RECOVERY_TIMEOUT = 10

last_failure_time = None


# ---------- External Service ----------
def external_service():

    success = random.choice(
        [True, False]
    )

    if not success:
        raise Exception(
            "Service unavailable"
        )

    return "Success"


# ---------- Protected Call ----------
@app.route("/call")
def call_service():

    global circuit_state
    global failure_count
    global last_failure_time

    # OPEN State
    if circuit_state == "OPEN":

        if (
            time.time()
            - last_failure_time
        ) > RECOVERY_TIMEOUT:

            circuit_state = "HALF_OPEN"

        else:

            return jsonify({
                "status":
                "Circuit OPEN"
            }), 503

    try:

        result = external_service()

        failure_count = 0

        circuit_state = "CLOSED"

        return jsonify({
            "result": result,
            "state": circuit_state
        })

    except Exception:

        failure_count += 1

        if (
            failure_count
            >= FAILURE_THRESHOLD
        ):

            circuit_state = "OPEN"

            last_failure_time = time.time()

        return jsonify({
            "error":
            "Service failed",
            "failures":
            failure_count,
            "state":
            circuit_state
        }), 500


# ---------- Circuit Status ----------
@app.route("/status")
def status():

    return jsonify({
        "state": circuit_state,
        "failures": failure_count
    })


# ---------- Health ----------
@app.route("/health")
def health():

    return jsonify({
        "status":
        "healthy"
    })


if __name__ == "__main__":

    app.run(debug=True)
