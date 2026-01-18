# Vanna Frontend

Next.js 15.5.7 ve React 19.2.1 ile geliştirilmiş Vanna AI frontend uygulaması.

## Özellikler

- 🔐 Kullanıcı kimlik doğrulama (Login/Register)
- 💬 SQL sorguları oluşturma ve çalıştırma
- 📝 Kaydedilmiş sorguları görüntüleme ve yönetme
- 🎨 Modern ve kullanıcı dostu arayüz
- 🏗️ SOLID prensiplerine uygun mimari
- 🔧 Maintainable ve test edilebilir kod yapısı

## Teknolojiler

- **Next.js**: 15.5.7
- **React**: 19.2.1
- **TypeScript**: Type safety için
- **Tailwind CSS**: Styling için

## Kurulum

```bash
# Bağımlılıkları yükle
npm install

# Development server'ı başlat
npm run dev

# Production build
npm run build

# Production server'ı başlat
npm start
```

## Yapı

Proje SOLID prensiplerine uygun olarak organize edilmiştir:

- `lib/`: API client, types, config, errors
- `context/`: React Context providers
- `hooks/`: Custom React hooks
- `components/`: UI components (UI, Auth, Chat, Queries)
- `app/`: Next.js app router pages

## Environment Variables

`.env.local` dosyası oluşturun:

```
NEXT_PUBLIC_API_URL=http://localhost:8084
```

## Mimari Prensipleri

### SOLID Principles

1. **Single Responsibility**: Her modül/component tek bir sorumluluğa sahiptir
2. **Open/Closed**: Component'ler props ile genişletilebilir, değiştirilemez
3. **Liskov Substitution**: Interface'ler doğru şekilde implement edilir
4. **Interface Segregation**: Küçük, odaklanmış interface'ler
5. **Dependency Inversion**: Yüksek seviye modüller abstraction'lara bağımlı

### Maintainability

- Type safety (TypeScript)
- Modüler yapı
- Separation of concerns
- Dependency injection
- Error handling
- Clean code practices
