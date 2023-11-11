from jmcomic import *
from jmcomic.cl import get_env, JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
410424
424020
407864
429914
503008
255392
203552
472851
341806
376159
457524
246656
294823
295843
'''

# 单独下载章节
jm_photos = '''

'''


def get_id_set(env_name):
    aid_set = set()
    for text in [
        jm_albums,
        (get_env(env_name, '')).replace('-', '\n'),
    ]:
        aid_set.update(str_to_set(text))

    return aid_set


def main():
    album_id_set = get_id_set('JM_ALBUM_IDS')
    photo_id_set = get_id_set('JM_PHOTO_IDS')

    helper = JmcomicUI()
    helper.album_id_list = list(album_id_set)
    helper.photo_id_list = list(photo_id_set)

    option = get_option()
    helper.run(option)
    option.call_all_plugin('after_download')

def get_option():
    # 读取 option 配置文件
    option = create_option('../assets/option/option_workflow_download.yml')

    # 支持工作流覆盖配置文件的配置
    cover_option_config(option)

    # 把请求错误的html下载到文件，方便GitHub Actions下载查看日志
    log_before_raise()

    return option


def cover_option_config(option: JmOption):
    dir_rule = get_env('DIR_RULE', None)
    if dir_rule is not None:
        the_old = option.dir_rule
        the_new = DirRule(dir_rule, base_dir=the_old.base_dir)
        option.dir_rule = the_new

    impl = get_env('CLIENT_IMPL', None)
    if impl is not None:
        option.client.impl = impl

    suffix = get_env('IMAGE_SUFFIX', None)
    if suffix is not None:
        option.download.image.suffix = fix_suffix(suffix)


def log_before_raise():
    jm_download_dir = get_env('JM_DOWNLOAD_DIR', workspace())
    mkdir_if_not_exists(jm_download_dir)

    # 自定义异常抛出函数，在抛出前把HTML响应数据写到下载文件夹（日志留痕）
    def raises(old, msg, extra: dict):
        if ExceptionTool.EXTRA_KEY_RESP not in extra:
            return old(msg, extra)

        resp = extra[ExceptionTool.EXTRA_KEY_RESP]
        # 写文件
        from common import write_text, fix_windir_name
        write_text(f'{jm_download_dir}/{fix_windir_name(resp.url)}', resp.text)

        return old(msg, extra)

    # 应用函数
    ExceptionTool.replace_old_exception_executor(raises)


if __name__ == '__main__':
    main()
