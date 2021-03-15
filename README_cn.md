# Tailor
[![GitHub license](https://img.shields.io/badge/license-Apache--2.0-brightgreen.svg)](https://github.com/bytedance/tailor/blob/master/LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Android-brightgreen.svg)](https://developer.android.com)
[![API](https://img.shields.io/badge/api-14%2B-green)](https://developer.android.com/about/dashboards)

Tailor是西瓜Android团队开发的一款通用内存快照裁剪压缩工具，通过它可以在异常时直接dump出一个迷你内存快照。快照中没
有任何敏感信息，更重要的是文件非常小的同时数据也相对完整，非常适合离线分析OOM及其他类型异常的调查定位。

## Apps using Tailor

| <img src="docs/xigua.png" alt="xigua" width="100"/> | <img src="docs/douyin.png" alt="douyin" width="100"/> | <img src="docs/huoshan.png" alt="huoshan" width="100"/> | <img src="docs/kaiyan.png" alt="kaiyan" width="100"/>
|:---------:|:-------:|:-------:|:-------:|
|  西瓜视频  |   抖音   |   火山  | 开言英语  |

## Get started

Step1 添加依赖：
```gradle
implementation 'com.bytedance.tailor:library:1.0.8'
```

Step2 代码接入：
```Java
// 在异常回调里通过Tailor获取快照，不同的app异常回调接口不同，可以根据app的实际情况调整，Ex：
Thread.setDefaultUncaughtExceptionHandler(new Thread.UncaughtExceptionHandler() {
    @Override
    public void uncaughtException(Thread t, Throwable e) {
        String path = Environment.getExternalStorageDirectory().getAbsolutePath() + File.separator + "mini.hprof";
        try {
            Tailor.dumpHprofData(path, true);
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
})
```

```Java
// 也可以直接对已经存在的hprof文件裁剪压缩
Tailor.cropHprofData(source, target, true);
```

Step3 数据上传：
```shell
应用需自己实现上传逻辑或相应的数据回捞功能
```

Step4 数据还原：
```shell
// 还原快照文件（Python version 3.5以上）
python3 library/src/main/python/decode.py -i mini.hprof -o target.hprof
```

## Extra

为了方便大家理解内存快照的文件格式及裁剪压缩细节，我们提供了三个脚本实现（Python version 3.5以上）
```shell
// 解析验证
python3 library/src/main/python/verify.py -i source.hprof

// 裁剪压缩
python3 library/src/main/python/encode.py -i source.hprof -o mini.hprof

// 数据还原
python3 library/src/main/python/decode.py -i mini.hprof -o target.hprof
```
## Support

1. 在[GitHub issues](https://github.com/bytedance/tailor/issues)上交流
2. 邮件: <a href="mailto:shentianzhou.stz@gmail.com">shentianzhou.stz@gmail.com</a>
3. 微信: 429013449
<p align="left"><img src="docs/wechat.jpg" alt="Wechat group" width="320px"></p>

## License
~~~
Copyright (c) 2020 ByteDance Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
~~~