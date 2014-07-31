#Load generator configuration
ENALBLE_FLOATING_IP=False
FLOATING_IP='150.165.85.73;150.165.85.74;150.165.85.75;150.165.85.76;150.165.85.77;150.165.85.78;'
LOAD_GENERATOR_ADDR="150.165.85.225"
LOAD_GENERATOR_PORT="5557"

#Monitor configuration
NOVA_PORT="8774"
CEILOMETER_PORT="8777"
KEYSTONE_PORT="5000"
USER_PASSWORD="fabiostack123"
OPENSTACK_CONF_FILE="../conf/AutoFlex-openrc.sh"
MONITORING_PERIOD=300
DATABASE_USER="stack"
DATABASE_PASSWORD="123"
DATABASE_PORT="3306"
DATABASE_ADDR="150.165.85.225"
DATABASE_DB_NAME="openstack"
METRIC_TYPE="cpu_util"

#Controller configuration
BASE_LENGHT=2016
BILLING_PERIOD=3600
CONTROL_PERIODICITY=300
SELECTION_PERIODICITY=86400
SELECTION_DATA_LENGTH=2016
MAX_INSTANCE_NUMBER=None
MIN_INSTANCE_NUMBER=1
FLAVOR_TYPE="m1.tiny"
FLAVOR_ID=""
IMAGE_ID=""
IMAGE_NAME="ubuntu_server"
PREDICTOR_TYPE="LW;AC;LR;AR;ARIMA;EN"
PREDICTOR_DATA_LEN='1;' + str(BASE_LENGHT) + ';' + str(BASE_LENGHT) + ';' + str(BASE_LENGHT) + ';' + str(BASE_LENGHT) +';1'
PREDICTION_HORIZON=600
REFERENCE_VALUE=0.7
VIOLATION_VALUE=0.99

#
CLOUD_PROD=True
