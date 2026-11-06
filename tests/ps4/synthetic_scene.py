"""Literal data-free observations at the public scene-to-seed boundary."""
import json

from synthetic_pipeline import make_model_collection


def make_scene_collection(directory, *, ocean=True, keys=(84, 126)):
    metadata = make_model_collection(directory, keys=keys)
    names = (['day', 'night', 'dense-fog', 'range-adjusted', 'camera-raised', 'day-repeated'] if ocean
             else ['untextured', 'textured', 'sloped-raised', 'textured-repeated'])
    layout = {'key': 16288162637680331091, 'attachments': 1, 'color_format': 27,
              'depth_format': 48, 'samples': 1, 'width': 1280, 'height': 720}
    metadata.update(scenario='scene-ocean-world-v1' if ocean else 'scene-simple-shadows-v1',
                    method='scripted-scene-draw', resource='/res/Object/Always.arc',
                    script={'states': names, 'frames_per_state': 1, 'setup': 'fixed-scene-world-camera-v1'},
                    frames=len(names), draw_calls=len(names), pipeline_lookups=len(names),
                    unhandled_states=['stage-and-weather-controllers', 'wave-simulation', 'real-shadow-receivers',
                                      'mirrors-and-reflections', 'other-camera-and-effect-combinations'],
                    resources={path: {'sha256': 'd' * 64, 'bytes': 100} for path in
                               ['/res/Object/Always.arc', '/res/Object/System.arc']},
                    contract_sha256='f' * 64, layout=layout,
                    preparation_layouts=[{'role': 'scene', **layout}, {'role': 'offscreen', **layout}],
                    states=[{'tick': i + 1, 'state': name, 'draw_calls': 1, 'pipeline_lookups': 1,
                             'layout_keys': [16288162637680331091],
                             'configurations': [{'type': 0, 'hash': keys[i % len(keys)]}]}
                            for i, name in enumerate(names)])
    (directory / 'collection.json').write_text(json.dumps(metadata))
    return metadata
