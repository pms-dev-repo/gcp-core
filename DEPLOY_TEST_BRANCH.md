# GCP integrated header test branch

Suggested branch: `feature/integrated-header`

```bash
git switch main
git pull origin main
git switch -c feature/integrated-header
```

Copy the files from this package, then test:

```bash
python -m streamlit run app.py
```

Commit and publish:

```bash
git add app.py components/header.py components/sidebar.py utils/styles.py
git commit -m "Integrate sidebar toggle into GCP header"
git push -u origin feature/integrated-header
```

Create a second Streamlit Community Cloud app using the same repository, branch `feature/integrated-header`, and main file `app.py`. Use a different app URL and copy the required secrets into the new app. Keep the production app connected to `main`.
