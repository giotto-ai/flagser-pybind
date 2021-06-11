import os
from tempfile import mkdtemp
from urllib.request import urlopen, urlretrieve

from pyflagser.modules.flagser_pybind import AVAILABLE_FILTRATIONS

files_with_filtration_results = ["d5.flag"]
large_files = ['medium-test-data.flag', 'd10.flag']


def pytest_addoption(parser):
    parser.addoption("--webdl", action="store_true", default=False,
                     help="Whether or not to download files "
                          "required for testing from the web")


class FlagFiles:
    paths = None


def fetch_flag_files(webdl):
    if not webdl:
        dirname = os.path.join(os.path.dirname(__file__), "../../flagser/test")
        try:
            fnames = os.listdir(dirname)
            flag_files = [os.path.join(dirname, fname) for fname in fnames
                          if fname.endswith(".flag")]
            return flag_files
        except FileNotFoundError:
            print(f".flag files looked for in {dirname}, but directory does "
                  "not exist. Pass the optional argument --webdl to "
                  "automatically download these files into a temporary "
                  "folder and run tests.")
    else:
        # Download from remote bucket
        temp_dir = mkdtemp()
        bucket_url = "https://storage.googleapis.com/l2f-open-models/" \
                     "giotto-tda/flagser/test/"
        flag_files_list = bucket_url + "flag_files_list.txt"
        with urlopen(flag_files_list) as f:
            flag_file_names = f.read().decode("utf8").splitlines()
            flag_files = []
            for fname in flag_file_names:
                url = bucket_url + fname
                fpath = os.path.join(temp_dir, fname)
                urlretrieve(url, fpath)
                flag_files.append(fpath)
        return flag_files


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    if FlagFiles.paths is None:
        webdl = metafunc.config.option.webdl
        FlagFiles.paths = fetch_flag_files(webdl)
    paths = FlagFiles.paths
    if "filtration" in metafunc.fixturenames:
        metafunc.parametrize("filtration", AVAILABLE_FILTRATIONS)
        paths = [p for p in paths
                 if os.path.split(p)[1] in files_with_filtration_results]
    if "flag_file" in metafunc.fixturenames:
        metafunc.parametrize("flag_file", paths)
    elif "flag_file_small" in metafunc.fixturenames:
        paths = [p for p in paths if os.path.split(p)[1] not in large_files]
        metafunc.parametrize("flag_file_small", paths)
