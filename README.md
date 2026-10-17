# SpotArchive for Windows

ابزارهای محلی و امن برای فایل‌های دارای مجوز `.spot`. این مخزن سازوکار رمزگذاری یا مجوز SpotPlayer را دور نمی‌زند.

## باز کردن فایل ویدئویی

پروژهٔ WinForms با نام **SpotArchive.Windows** یک رابط ساده برای انتخاب یا کشیدن‌ورهای فایل `.spot` است. پس از انتخاب، فایل را به برنامهٔ ثبت‌شده در ویندوز (SpotPlayer رسمی) می‌سپارد.

فایل‌های `.spot`، ویدیوی استاندارد مانند MP4 نیستند؛ برای پخش به نصب SpotPlayer رسمی و مجوز معتبر ناشر محتوا نیاز دارید.

### اجرا

پیش‌نیاز: [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0) در ویندوز.

```powershell
dotnet run --project .\SpotArchive.Windows.csproj
```

ساخت فایل اجرایی مستقل:

```powershell
dotnet publish .\SpotArchive.Windows.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
```

## بایگانی و نسخهٔ پشتیبان

`spotarchive.py` ابزار قبلی مخزن است که پوشه‌های دانلود SpotPlayer را فقط فهرست می‌کند و پشتیبان SHA-256 تأییدشده می‌سازد؛ هیچ فایلی را پاک، آپلود یا رمزگشایی نمی‌کند.

برای اجرای آن در ویندوز (Python 3.10+):

```powershell
python spotarchive.py
```

همیشه فایل اصلی و اطلاعات مجوز را خصوصی نگه دارید و تا مطمئن شدن از پخش، نسخهٔ اصلی را حذف نکنید.
