# Replace JSON Key Values

This GitHub Action replaces key values inside JSON files using a simple `Object.Key=value` syntax.  
It is designed for dynamically updating configuration files (e.g., `appsettings.json`) in your CI/CD workflows.

---

## 📦 Inputs

### `files` (required)
List of JSON files where values will be replaced.  
Files must be separated by `|`.

**Example:**
```yaml
files: "config.json|secrets.json"
```

### `replacements` (required)

Pairs of `Object.Key=value` separated by `|`.  
Supports nested keys, literal keys, and automatic type casting (`number`, `boolean`, `null`, strings).

**Example:**
```yaml
replacements: "Database.Host=localhost|Database.Port=1433|FeatureFlags.EnableCache=true"
```

## ⚙️ Usage Example

```yaml
name: Update JSON Config

on:
  push:
    branches: [ "main" ]

jobs:
  replace-json:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Replace values in JSON
        uses: georguiazel/template-actions-replace@v4
        with:
          files: "${{ github.workspace }}/config/appsettings.json"
          replacements: |
            Database.Host=prod-db.example.com|
            Database.User=${{ secrets.DB_USER }}|
            Database.Password=${{ secrets.DB_PASSWORD }}|
            FeatureFlags.EnableCache=false
```

## 🛠 Author
Developed by **[georguiazel](https://github.com/georguiazel)**