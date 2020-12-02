from jsonschema import validate
import json

from src.modules.create_graph.config import config_parser


class ErrorHandling:
    slo_case = {'SLO', 'PS', 'HP'}

    def check_organization(self, input_data):
        '''
         Organization ce je slo-cro/ ps hp
        '''
        if input_data['event'] is None:
            return

        if input_data['organization'] == 'ELTA':
            if input_data['event']['event_type'] != 'vehicle':
                for item in input_data['event']['info']['items']:
                    if item['organization'] != 'ELTA':
                        raise ValueError("Wrong organization. Organization should be the same at the same message")

            for clo in input_data['clos']:
                if clo['info']['organization'] != 'ELTA':
                    raise ValueError("Wrong organization. Organization should be the same at the same message")

            for parcel in input_data['parcels']:
                if parcel['organization'] != 'ELTA':
                    raise ValueError("Wrong organization. Organization should be the same at the same message")

        if input_data['organization'] == 'PS':
            if input_data['event']['event_type'] != 'vehicle':
                for item in input_data['event']['info']['items']:
                    if item['organization'] not in self.slo_case:
                        raise ValueError("Wrong organization. Organization should be the same at the same message")

            for clo in input_data['clos']:
                if clo['info']['organization'] not in self.slo_case:
                    raise ValueError("Wrong organization. Organization should be the same at the same message")

            for parcel in input_data['parcels']:
                if parcel['organization'] not in self.slo_case:
                    raise ValueError("Wrong organization. Organization should be the same at the same message")

    def check_complited_plan(self, input_data):
        '''
         daily plan -> complited plan prazn oz missing
        '''

        for clo in input_data['clos']:
            if 'completed_plan' not in clo['state']:
                raise ValueError("Completed plan is missing")

    def check_locations(self, input_data):

        if input_data['organization'] == "PS" or \
                input_data['organization'] == "HP":
            use_case_graph = config_parser.ConfigParser()
            fObj = open(use_case_graph.get_csv_path("SLO-CRO_crossborder"))

            nodes = json.load(fObj)['nodes']
            node_dict = {}
            for node in nodes:
                value = nodes[node]
                node_dict[value['uuid']] = {'lat': value['lat'], 'lon': value['lon']}

            for clo in input_data['clos']:
                print(clo['state']['location'])
                if clo['state']['location']['station'] not in node_dict or \
                        clo['state']['location']['latitude'] != node_dict[clo['state']['location']['station']]['lat'] or \
                        clo['state']['location']['longitude'] != node_dict[clo['state']['location']['station']]['lon']:
                    raise ValueError("Check lat, lon and uuid. It doesnt exists in our database {}"
                                     .format(clo['state']['location']))

            for clo in input_data['parcels']:
                print(clo)
                if clo['source']['station'] not in node_dict or \
                        clo['source']['latitude'] != node_dict[clo['source']['station']]['lat'] or \
                        clo['source']['longitude'] != node_dict[clo['source']['station']]['lon']:
                    raise ValueError(
                        "Check lat, lon and uuid. It doesnt exists in our database {}".format(clo['source']))

                if clo['destination']['station'] not in node_dict or \
                        clo['destination']['latitude'] != node_dict[clo['destination']['station']]['lat'] or \
                        clo['destination']['longitude'] != node_dict[clo['destination']['station']]['lon']:
                    raise ValueError(
                        "Check lat, lon and uuid. It doesnt exists in our database {}".format(clo['destination']))

                '''
                a = clo['state']['location']['latitude']
                b = node_dict[clo['state']['location']['station']]['lat']
                '''

        if input_data['organization'] == "SLO-CRO":
            pass

    def check_event(self, input_data):
        event_types = {'order', 'vehicle', 'border'}
        if input_data['event'] is None:
            return

        if 'event_type' not in input_data['event'] :
            raise ValueError("Event type is missing")

        if input_data['event']['event_type'] not in event_types:
            raise ValueError("Wrong event type.")

    def check_payweight(self, input_data):
        for clo in input_data['parcels']:
            print(clo)
            if 'payweight' not in clo or clo['payweight'] != 1:
                raise ValueError("Payweight is missing.")

    def check_parcel_clos(self, input_data):
        if 'parcels' not in input_data or \
                type(input_data['parcels']) is not list or \
                'clos' not in input_data or \
                type(input_data['clos']) is not list:
            raise ValueError("Parcels and Clos wrong type.")

    def chech_parcel_id(self, input_data):
        l = []
        for clo in input_data['parcels']:
            l.append(clo["id"])

        if len(l) != len(set(l)):
            raise ValueError("Parcelid are not unique.")


    def check_messages_correction(self, input_data):

        self.check_event(input_data)
        self.check_organization(input_data)

        self.check_complited_plan(input_data)

        self.check_locations(input_data)

        self.check_payweight(input_data)
        self.check_parcel_clos(input_data)

        self.chech_parcel_id(input_data)
