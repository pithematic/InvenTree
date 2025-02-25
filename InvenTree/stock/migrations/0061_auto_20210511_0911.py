# Generated by Django 3.2 on 2021-05-10 23:11

import re

from django.db import migrations

from InvenTree.status_codes import StockHistoryCode


def update_history(apps, schema_editor):
    """
    Update each existing StockItemTracking object,
    convert the recorded "quantity" to a delta
    """

    StockItem = apps.get_model('stock', 'stockitem')
    StockItemTracking = apps.get_model('stock', 'stockitemtracking')
    StockLocation = apps.get_model('stock', 'stocklocation')

    update_count = 0

    locations = StockLocation.objects.all()

    for location in locations:  # pragma: no cover
        # Pre-calculate pathstring
        # Note we cannot use the 'pathstring' function here as we don't have access to model functions!

        path = [location.name]

        loc = location

        while loc.parent:
            loc = loc.parent
            path = [loc.name] + path

        location._path = '/'.join(path)

    for item in StockItem.objects.all():  # pragma: no cover

        history = StockItemTracking.objects.filter(item=item).order_by('date')

        if history.count() == 0:
            continue

        quantity = history[0].quantity

        for idx, entry in enumerate(history):

            deltas = {}
            updated = False

            q = entry.quantity

            if idx == 0 or not q == quantity:

                try:
                    deltas['quantity']: float(q)
                    updated = True
                except:
                    print(f"WARNING: Error converting quantity '{q}'")


            quantity = q

            # Try to "guess" the "type" of tracking entry, based on the title
            title = entry.title.lower()

            tracking_type = None

            if 'completed build' in title:
                tracking_type = StockHistoryCode.BUILD_OUTPUT_COMPLETED

            elif 'removed' in title and 'item' in title:

                if entry.notes.lower().startswith('split '):
                    tracking_type = StockHistoryCode.SPLIT_CHILD_ITEM
                else:
                    tracking_type = StockHistoryCode.STOCK_REMOVE

                # Extract the number of removed items
                result = re.search(r"^removed ([\d\.]+) items", title)

                if result:

                    removed = result.groups()[0]

                    try:
                        deltas['removed'] = float(removed)

                        # Ensure that 'quantity' is stored too in this case
                        deltas['quantity'] = float(q)
                    except:
                        print(f"WARNING: Error converting removed quantity '{removed}'")
                else:
                    print(f"Could not decode '{title}'")

            elif 'split from existing' in title:
                tracking_type = StockHistoryCode.SPLIT_FROM_PARENT

                deltas['quantity'] = float(q)

            elif 'moved to' in title:
                tracking_type = StockHistoryCode.STOCK_MOVE

                result = re.search(r'^Moved to (.*)( - )*(.*) \(from.*$', entry.title)

                if result:
                    # Legacy tracking entries recorded the location in multiple ways, because.. why not?
                    text = result.groups()[0]

                    matches = set()

                    for location in locations:

                        # Direct match for pathstring
                        if text == location._path:
                            matches.add(location)

                        # Direct match for name
                        if text == location.name:
                            matches.add(location)

                        # Match for "name - description"
                        compare = f"{location.name} - {location.description}"

                        if text == compare:
                            matches.add(location)

                        # Match for "pathstring - description"
                        compare = f"{location._path} - {location.description}"

                        if text == compare:
                            matches.add(location)

                    if len(matches) == 1:
                        location = list(matches)[0]

                        deltas['location'] = location.pk

                    else:
                        print(f"No location match: '{text}'")
                        break

            elif 'created stock item' in title:
                tracking_type = StockHistoryCode.CREATED

            elif 'add serial number' in title:
                tracking_type = StockHistoryCode.ASSIGNED_SERIAL

            elif 'returned from customer' in title:
                tracking_type = StockHistoryCode.RETURNED_FROM_CUSTOMER

            elif 'counted' in title:
                tracking_type = StockHistoryCode.STOCK_COUNT

            elif 'added' in title:
                tracking_type = StockHistoryCode.STOCK_ADD

                # Extract the number of added items
                result = re.search(r"^added ([\d\.]+) items", title)

                if result:

                    added = result.groups()[0]

                    try:
                        deltas['added'] = float(added)

                        # Ensure that 'quantity' is stored too in this case
                        deltas['quantity'] = float(q)
                    except:
                        print(f"WARNING: Error converting added quantity '{added}'")

                else:
                    print(f"Could not decode '{title}'")

            elif 'assigned to customer' in title:
                tracking_type = StockHistoryCode.SENT_TO_CUSTOMER

            elif 'installed into stock item' in title:
                tracking_type = StockHistoryCode.INSTALLED_INTO_ASSEMBLY

            elif 'uninstalled into location' in title:
                tracking_type = StockHistoryCode.REMOVED_FROM_ASSEMBLY

            elif 'installed stock item' in title:
                tracking_type = StockHistoryCode.INSTALLED_CHILD_ITEM

            elif 'received items' in title:
                tracking_type = StockHistoryCode.RECEIVED_AGAINST_PURCHASE_ORDER

            if tracking_type is not None:
                entry.tracking_type = tracking_type
                updated = True

            if updated:
                entry.deltas = deltas
                entry.save()
                update_count += 1


    if update_count > 0:
        print(f"\n==========================\nUpdated {update_count} StockItemHistory entries")  # pragma: no cover


def reverse_update(apps, schema_editor):
    """
    """
    pass  # pragma: no cover


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0060_auto_20210511_1713'),
    ]

    operations = [
        migrations.RunPython(update_history, reverse_code=reverse_update)
    ]
