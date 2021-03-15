# Tailor

[简体中文版说明 >>>](/README_cn.md)

[![GitHub license](https://img.shields.io/badge/license-Apache--2.0-brightgreen.svg)](https://github.com/bytedance/tailor/blob/master/LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Android-brightgreen.svg)](https://developer.android.com)
[![API](https://img.shields.io/badge/api-14%2B-green)](https://developer.android.com/about/dashboards)

Tailor is a general-purpose hprof cropping and compression tool developed by Xigua video android
team. Through it, a mini hprof file can be dump directly during exception handling. There is no
sensitive information in the file。More importantly, the file is small but the data is relatively
complete, which is very suitable for offline analysis of oom and other exceptions

## Apps using Tailor

| <img src="docs/xigua.png" alt="xigua" width="100"/> | <img src="docs/douyin.png" alt="douyin" width="100"/> | <img src="docs/huoshan.png" alt="huoshan" width="100"/> | <img src="docs/kaiyan.png" alt="kaiyan" width="100"/>
|:-----------:|:-------:|:-------:|:-------:|
| Xigua Video | Douyin  | Huoshan | Kaiyan  |

## Get started

Step1: Add to your build.gradle
```gradle
implementation 'com.bytedance.tailor:library:1.0.8'
```

Step2: For simple usage

```java
// Using Tailor to get a mini hprof file in exception callback
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
// Crop and compress the existing hprof files directly
Tailor.cropHprofData(source, target, true);
```

Step3: File upload
```shell
App needs to implement upload logic by itself
```

Step4: Data recovery(Python version 3.5 and above)
```shell
python3 library/src/main/python/decode.py -i mini.hprof -o target.hprof
```

## Extra

In order to facilitate everyone to understand the file format of the hprof and the details of cropping
and compression, we provide three script implementations (Python version 3.5 and above)

```shell
// Hprof verify
python3 library/src/main/python/verify.py -i source.hprof

// Crop and compress
python3 library/src/main/python/encode.py -i source.hprof -o mini.hprof

// Data recovery
python3 library/src/main/python/decode.py -i mini.hprof -o target.hprof
```
## Support

1. Communicate on [GitHub issues](https://github.com/bytedance/tailor/issues)
2. Mail: <a href="mailto:shentianzhou.stz@gmail.com">shentianzhou.stz@gmail.com</a>
3. WeChat: 429013449
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