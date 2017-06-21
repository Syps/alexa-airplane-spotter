from __future__ import print_function
from nearby import nearby
from logger import logger
import json

NO_NEARBY_OUTPUT_SPEECH = "Sorry, I'm not seeing any nearby planes at the moment"


def speech_output(plane_data):
    logger.info('getting speech output for {}'.format(plane_data))
    output = "That's {airline_article} {airline} {aircraft}"
    route_output = " going from {depart_airport} to {arrival_airport}"

    from_airport = plane_data.get('airport_depart', None)
    to_airport = plane_data.get('airport_arrive', None)

    airline = plane_data.get('airline', 'unknown airline')
    airline_article = 'an' if airline[0] in 'aieou' else 'a'
    aircraft = plane_data['aircraft']

    formatted_output = output.format(airline_article=airline_article, airline=airline, aircraft=aircraft)
    if not from_airport or not to_airport:
        return formatted_output
    else:
        formatted_route_output = route_output.format(depart_airport=from_airport, arrival_airport=to_airport)
        return formatted_output + formatted_route_output


def get_output_speech():
    flight = nearby()
    if not flight:
        print(NO_NEARBY_OUTPUT_SPEECH)
        return NO_NEARBY_OUTPUT_SPEECH
    result = speech_output(flight)
    print(result)
    return result


if __name__ == '__main__':
    get_output_speech()
