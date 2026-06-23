from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os

app = Flask(__name__)
CORS(app)

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    rtl_code = data.get('rtl', '')
    tb_code = data.get('testbench', '')

    with tempfile.TemporaryDirectory() as tmpdir:
        rtl_file = os.path.join(tmpdir, 'design.v')
        tb_file = os.path.join(tmpdir, 'testbench.v')
        out_file = os.path.join(tmpdir, 'sim.out')

        with open(rtl_file, 'w') as f:
            f.write(rtl_code)

        with open(tb_file, 'w') as f:
            f.write(tb_code)

        compile_result = subprocess.run(
            ['iverilog', '-g2012', '-o', out_file, rtl_file, tb_file],
            capture_output=True, text=True, timeout=30
        )

        if compile_result.returncode != 0:
            return jsonify({
                'success': False,
                'output': compile_result.stderr
            })

        sim_result = subprocess.run(
            ['vvp', out_file],
            capture_output=True, text=True, timeout=30
        )

        return jsonify({
            'success': True,
            'output': sim_result.stdout or sim_result.stderr
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
