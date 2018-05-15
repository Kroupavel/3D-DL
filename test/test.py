import sys
import os
import pathlib
import unittest
import coverage
import argparse
import subprocess
import site

# Ensure source directory is in python path
project_dir = str(pathlib.Path(__file__).parents[1].resolve())
sys.path.append(os.path.join(project_dir, 'src'))

# for keras
sys.path.append(project_dir)

""" --------------- CLI setup ------------- """
parser = argparse.ArgumentParser(description='Run all Ocado project tests and record coverage.')

parser.add_argument('-b', '--blender_tests', action='store_true',
                    help='run BlenderAPI tests (requires blender to be installed and in system path)')

parser.add_argument('-k', '--keras_tests', action='store_true',
                    help='run keras tests')

parser.add_argument('-l', '---scene_tests', action='store_true',
                    help='run RandomLib and SceneLib tests')

parser.add_argument('-p', '--pipeline_tests', action='store_true',
                    help='run pipeline tests')

parser.add_argument('-rt', '--report_tests', action='store_true',
                    help='include test files in coverage report')

parser.add_argument('-rb', '--report_branch', action='store_true',
                    help='include branch coverage (see XML report for detailed figures)')


args = parser.parse_args()

print(args)

""" --------------- Run blender tests ------------- """
if args.blender_tests:
    blender_script_dir = os.path.join(project_dir, 'test', 'test_blender.py')
    blender_args = ['blender', '--background', '--python', blender_script_dir,
                    '--', project_dir, site.getsitepackages()[0], str(args.report_branch)]

    print('Running Blender tests')
    subprocess.check_call(blender_args)
    print('Blender tests complete')


""" --------------- Configure Coverage.py ------------- """
coverage_data_dir = os.path.join(project_dir, 'test', 'coverage', 'data')
cov = coverage.Coverage(omit=['*lib*', '*__init__*'], branch=args.report_branch, data_file=coverage_data_dir)

cov.start()

""" --------------- Module Imports ------------- """
# Import keras
if args.keras_tests:
    from kerasmodels.testRetrainTest.keras_eval_test import KerasEvalTest
    from kerasmodels.retrain_unittest import TestKerasRetrain

if args.scene_tests:
    # Import randomLib
    from src.rendering.TestRandomLib.TestMetaballs import Testturbulence
    from src.rendering.TestRandomLib.TestRandomRender import Testturbulence as render_Testturbulence
    from src.rendering.TestRandomLib.TestTurbulence import Testturbulence as turbulence_Testturbulence
    from src.rendering.TestRandomLib.TestRandBack import TestResizeImages as rand_TestResizeImages

    # Import merge/resize
    from src.rendering.TestSceneLib.TestMergeResize import TestResizeImages

if args.pipeline_tests:
    from src.rendering.TestPipeline.TestRenderPipeline import TestPipeline


""" --------------- Load Tests Cases ------------- """
suites = []

# Load Keras
if args.keras_tests:
    suites.append(unittest.defaultTestLoader.loadTestsFromTestCase(TestKerasRetrain))


if args.scene_tests:
    # Load randomLib
    suites.append(unittest.defaultTestLoader.loadTestsFromTestCase(Testturbulence))
    suites.append(unittest.defaultTestLoader.loadTestsFromTestCase(render_Testturbulence))
    suites.append(unittest.defaultTestLoader.loadTestsFromTestCase(turbulence_Testturbulence))
    suites.append(unittest.defaultTestLoader.loadTestsFromTestCase(rand_TestResizeImages))

    # Load sceneLib
    suites.append(unittest.defaultTestLoader.loadTestsFromTestCase(TestResizeImages))

if args.pipeline_tests:
    suites.append(unittest.defaultTestLoader.loadTestsFromTestCase(TestPipeline))

""" --------------- Run tests ------------- """
tests = unittest.TestSuite(suites)
success = unittest.TextTestRunner().run(tests).wasSuccessful()

cov.stop()


""" ---------------Save and Combine Results ------------- """
cov.save()

if args.blender_tests:
    cov.combine(data_paths=[os.path.join(project_dir, 'test', 'coverage', 'data'),
                            os.path.join(project_dir, 'test', 'coverage', 'data_blender'),
                            os.path.join(project_dir, 'test', 'coverage', 'data_keras')])

omit = ['*testBlenderAPI*', '*TestRandomLib*', '*TestSceneLib*', '*test_*', '*retrain_unittest*']
if args.report_tests:
    omit = []

cov.report(omit=omit)

coverage_html_dir = os.path.join(project_dir, 'test', 'coverage', 'htmlcov')
coverage_xml_dir = os.path.join(project_dir, 'test', 'coverage', 'xmlcov', 'report.xml')
cov.html_report(omit=omit, directory=coverage_html_dir)
cov.xml_report(omit=omit, outfile=coverage_xml_dir)

