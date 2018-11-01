# Web page Downloader

import sys
import urllib.request
import urllib.error
import re
import os
import argparse

timeout_time = 2
search_level = 1
url = ""
file_format = ""
files_to_download = set()
save_directory = 'pyGrabber'


def is_sutable_for_download(file, format):
    if file.endswith(format):
        return True
    return False


def get_sutable_links(the_set, format):
    return set(filter(lambda x: is_sutable_for_download(x), the_set))


def find_links_of(url, search_level):
    print('\t' * search_level * (search_level-1) / 2)
    print(url)
    try:
        links = urllib.request.urlopen(url, timeout=timeout_time)
        links = links.read().decode('utf-8', 'ignore')
        link_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|\
                        (?:%[0-9a-fA-F][0-9a-fA-F]))+'
        links = re.findall(link_pattern, links)
        links = set(links)
        return links
    except urllib.error.URLError:
        print('\t' * search_level * (search_level-1) / 2)
        print("Passing the link because of URL is unreachable")
        return set()
    except KeyboardInterrupt:
        if input('\nAre you sure you want to quit (y/n)? : ') == 'y':
            sys.exit(0)
        print("Continue:")
        return set()
    except TimeoutError:
        print('\t' * search_level * (search_level-1) / 2)
        print("The read operation timed out")
        return set()


def is_url(__str__):
    if re.match(r'https?://(?:www)?(?:[\w-]{2,255}(?:\.\w{2,6}){1,2})\
                  (?:/[\w&%?#-]{1,300})?', __str__):
        return True
    return False


def url_file_size(url):
    try:
        url_request = urllib.request.urlopen(url, timeout=timeout_time)
        url_meta = url_request.info()
        url_size_in_bytes = url_meta.get(name="Content-Length")
        url_request.close()
        url_size_in_bytes = int(url_size_in_bytes)
        return url_size_in_bytes
    except ValueError as e:
        print("Cannot convert file size into int, there should be a \
               problem in headers")
        print(f"got this error: {e}")
    except TimeoutError as e:
        print(f"request timed out\n{e}")


def partial_download(url, step=100):
    total_size = url_file_size(url)
    response = bytes()
    current_size = 0
    while current_size < total_size:
        if (total_size - current_size) < step:
            step = total_size - current_size
        req = urllib.request.Request(url)
        req.headers['Range'] = f'bytes={current_size}-{current_size + step}'
        server_resp = urllib.request.urlopen(req)
        response += server_resp.read()
        server_resp.close()
        current_size += step
    return response


def downloading(all, reqs, save_dir):
    if len(all) == 0 or len(reqs) == 0:
        print('nothing found')
        sys.exit(0)
    print('from:')
    print(all)
    print('downloading:')
    print(reqs)
    print("total of ", end='')
    print(len(reqs), end='')
    if input("files will be downloaded start download (y/n) ?") == 'y':
        for x in reqs:
            print("downloading : ", end='')
            print(x)
            print('\tas : ', end='')
            print(x[x.rfind("/")+1:] + '\n')
            try:
                urllib.request.urlretrieve(x, save_dir + '/' +
                                           x[x.rfind("/")+1:])
            except urllib.error as e:
                print('Download Failed' + str(e))


def handle_arguments():
    parser = argparse.ArgumentParser()


def help():
    """
    function to help users how to work with program
    """
    print("grabbs files from a specified web page with specified format")
    print("usage: pyGrabber <website_url> <-f file_format> [-h] [-d save\
            directory] [-l search level]")
    print("\toptions:")
    print("\t\t-f format\tsearch the pages for files with this format")
    print("\t\t-d directory\tsaves the downloade files into this directory")
    print("\t\t-l level\tint number to define deapth of search default is 0")


if __name__ == '__main__':
    for x in range(len(sys.argv)):
        if "-h" in sys.argv or "--help" in sys.argv:
            help()
            sys.exit(0)
        if "-f" not in sys.argv or not is_url(sys.argv[1]):
            print("Bad input")
            sys.exit(0)
        if sys.argv[x-1] == '-l' or sys.argv[x-1] == '-f' or \
                sys.argv[x-1] == '-d':
            continue
        if sys.argv[x] == '-l':
            print('search level  : ', end='')
            print(sys.argv[x+1])
            search_level = int(sys.argv[x+1])
        elif is_url(sys.argv[x]):
            print("search url    : ", end='')
            print(sys.argv[x])
            url = sys.argv[x]
        elif sys.argv[x] == '-f':
            print("search format : ", end='')
            print(sys.argv[x+1])
            file_format = sys.argv[x+1]
            if not file_format.startswith('.'):
                file_format = '.' + file_format
        elif sys.argv[x] == '-d':
            print('saving into   : ', end='')
            print(sys.argv[x+1])
            save_directory = sys.argv[x+1]
            if not os.path.exists(save_directory):
                if input('directory does not exist create it (y/n)?: ') == 'y':
                    os.makedirs(save_directory)
                else:
                    sys.exit(0)

    file_content = {url}
    append_file_content = set()
    all_of_links = set()

    for x in range(search_level):
        all_of_links = all_of_links.union(file_content)
        files_to_download = files_to_download.union(get_sutable_links(
                    file_content, file_format))
        for y in file_content:
            new_links = find_links_of(y, x)
            append_file_content = append_file_content.union(new_links)

        append_file_content.discard(all_of_links)
        file_content = append_file_content
        append_file_content = set()

# downloading(file_content , files_to_download , save_directory)
    partial_download(url="http://ipv4.download.thinkbroadband.com/5MB.zip")
