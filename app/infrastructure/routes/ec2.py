import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.application.services.ec2 import EC2Service

logger = logging.getLogger(__name__)

ec2_bp = Blueprint('ec2', __name__, url_prefix='/ec2')

# EC2 Service instance
ec2_service = EC2Service()

@ec2_bp.route('/', methods=['GET'])
def index():
    """Renders the EC2 instances monitoring dashboard."""
    instances = ec2_service.list_instances()
    return render_template('ec2/index.html', instances=instances)

@ec2_bp.route('/create', methods=['POST'])
def create():
    """Launches a new mock EC2 instance on LocalStack."""
    name = request.form.get('name', '').strip()
    instance_type = request.form.get('instance_type', 't2.micro').strip()

    if not name:
        flash('Nama instance tidak boleh kosong!', 'danger')
        return redirect(url_for('ec2.index'))

    result = ec2_service.create_instance(name=name, instance_type=instance_type)
    if result:
        flash(f"EC2 Instance '{name}' ({result['instance_id']}) berhasil diluncurkan.", 'success')
    else:
        flash('Terjadi kesalahan saat meluncurkan EC2 instance di LocalStack.', 'danger')

    return redirect(url_for('ec2.index'))

@ec2_bp.route('/<string:id>/start', methods=['POST'])
def start(id):
    """Sends a start command to a stopped EC2 instance."""
    if ec2_service.start_instance(id):
        flash(f"Instruksi START berhasil dikirim ke instance '{id}'.", 'success')
    else:
        flash(f"Gagal mengirim instruksi START ke instance '{id}'.", 'danger')
    return redirect(url_for('ec2.index'))

@ec2_bp.route('/<string:id>/stop', methods=['POST'])
def stop(id):
    """Sends a stop command to a running EC2 instance."""
    if ec2_service.stop_instance(id):
        flash(f"Instruksi STOP berhasil dikirim ke instance '{id}'.", 'success')
    else:
        flash(f"Gagal mengirim instruksi STOP ke instance '{id}'.", 'danger')
    return redirect(url_for('ec2.index'))

@ec2_bp.route('/<string:id>/terminate', methods=['POST'])
def terminate(id):
    """Sends a terminate command to an EC2 instance."""
    if ec2_service.terminate_instance(id):
        flash(f"Instruksi TERMINATE berhasil dikirim ke instance '{id}'.", 'success')
    else:
        flash(f"Gagal mengirim instruksi TERMINATE ke instance '{id}'.", 'danger')
    return redirect(url_for('ec2.index'))
