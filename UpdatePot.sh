#ref : git_download.sh

#call xgettext to gen .pot
find . -type f -name '*.py' -print0 | xargs -0 xgettext --language=Python --keyword=LID --add-comments --output=ListenRepeater.pot --no-location --from-code=UTF-8

#call msgmerge to update *.po (from .pot)
msgmerge -U locale/zh_TW/LC_MESSAGES/ListenRepeater.po ListenRepeater.pot
msgmerge -U locale/en_US/LC_MESSAGES/ListenRepeater.po ListenRepeater.pot

echo
read -n1 -r -p "Press any key to close..." key